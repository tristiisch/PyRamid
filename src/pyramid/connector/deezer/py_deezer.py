import asyncio
import hashlib
import logging
from shlex import join
import warnings
from os import path

import aiofiles
import aiohttp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from data.exceptions import CustomException

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	from cryptography.hazmat.primitives.ciphers.algorithms import Blowfish

from pydeezer import Deezer, util
from pydeezer.constants import api_methods, api_urls, networking_settings, track_formats
from pydeezer.exceptions import APIRequestError, DownloadLinkDecryptionError, LoginError
from pydeezer.ProgressHandler import BaseProgressHandler, DefaultProgressHandler


class DlDeezerNotUrlFoundException(CustomException):
	pass


class DecryptDeezer:
	def __init__(self, blowfish_key: bytes, progress_handler: BaseProgressHandler) -> None:
		self.chunk_length = 6144
		self.decrypt_chunk_length = 2048
		self.cipher = Cipher(
			Blowfish(blowfish_key),
			modes.CBC(bytes([i for i in range(8)])),
			default_backend(),
		)
		self.f: aiofiles.threadpool.binary.AsyncBufferedIOBase
		self.progress_handler = progress_handler

	async def output_file(self, filesize: int, file_path: str, res: aiohttp.ClientResponse):
		async with aiofiles.open(file_path, "wb") as f:
			self.f = f
			await f.seek(0)

			chunk_index = 0
			downloaded_size = 0
			previous_chunk = None
			async for chunk, _ in res.content.iter_chunks():
				chunk_size = len(chunk)
				self.progress_handler.update(current_chunk_size=chunk_size)

				downloaded_size += chunk_size
				if previous_chunk:
					previous_chunk, chunks_used = await self._transform_chunk(
						previous_chunk + chunk
					)
				else:
					previous_chunk, chunks_used = await self._transform_chunk(chunk)
				chunk_index += chunks_used

			if previous_chunk:
				await self._write_file(previous_chunk)
			if downloaded_size != filesize:
				missing = filesize - downloaded_size
				raise Exception("[%s] %d bytes are missing" % (filesize, missing))

	async def _transform_chunk(self, bytes_chunked: bytes) -> tuple[bytes, int] | tuple[None, int]:
		# Calculate the number of chunks needed
		length_bytes = len(bytes_chunked)
		chunks_nb = int(length_bytes / self.chunk_length) + 1

		# Iterate over the chunks and call the callback for each one
		for i in range(chunks_nb - 1):
			chunk = bytes_chunked[i * self.chunk_length : (i + 1) * self.chunk_length]
			await self._write_file(chunk)

		last_chunk_start = (chunks_nb - 1) * self.chunk_length
		last_chunk = bytes_chunked[last_chunk_start:]
		last_length = len(last_chunk)

		if last_length == self.chunk_length:
			await self._write_file(last_chunk)
			return None, chunks_nb
		elif last_length < self.chunk_length:
			return last_chunk, chunks_nb - 1
		raise Exception(
			"Last chunk has wrong size %d (under %d is excepted)", last_length, self.chunk_length
		)

	async def _write_file(self, new_chunk: bytes):
		chunk_size = len(new_chunk)
		if self.decrypt_chunk_length > chunk_size:
			await self.f.write(new_chunk)
		else:
			chunk_to_decrypt = new_chunk[: self.decrypt_chunk_length]
			decryptor = self.cipher.decryptor()
			dec_data = decryptor.update(chunk_to_decrypt) + decryptor.finalize()
			await self.f.write(dec_data)
			await self.f.write(new_chunk[self.decrypt_chunk_length :])


class PyDeezer(Deezer):
	def __init__(self, arl=None):
		super().__init__()
		self.arl = arl
		self.token = None
		self.set_cookie("arl", arl)

	async def download_track(
		self,
		track,
		download_dir,
		quality=None,
		fallback=True,
		filename=None,
		renew=False,
		with_metadata=True,
		with_lyrics=True,
		tag_separator=", ",
		show_messages=True,
		progress_handler: BaseProgressHandler | None = None,
		**kwargs,
	):
		if with_lyrics:
			if "LYRICS" in track:
				lyric_data = track["LYRICS"]
			else:
				try:
					# TODO Make it async
					if "DATA" in track:
						lyric_data = self.get_track_lyrics(track["DATA"]["SNG_ID"])["info"]
					else:
						lyric_data = self.get_track_lyrics(track["SNG_ID"])["info"]
				except APIRequestError:
					with_lyrics = False

		track = track["DATA"] if "DATA" in track else track

		res = await self.get_track_download_url(
			track, quality, fallback=fallback, renew=renew, **kwargs
		)
		url, quality_key = res

		blowfish_key = util.get_blowfish_key(track["SNG_ID"])

		# quality = self._select_valid_quality(track, quality)

		quality = track_formats.TRACK_FORMAT_MAP[quality_key]

		title = track["SNG_TITLE"]
		ext = quality["ext"]

		if not filename:
			filename = title + ext

		if not str(filename).endswith(ext):
			filename += ext

		filename = util.clean_filename(filename)

		download_dir = path.normpath(download_dir)
		download_path = path.join(download_dir, filename)

		util.create_folders(download_dir)

		if show_messages:
			print("Starting download of:", title)

		async with aiohttp.ClientSession() as session:
			async with session.get(
				url,
				cookies=self.get_cookies(),
				timeout=None,
				headers=networking_settings.HTTP_HEADERS,
				chunked=True,
				ssl=None,
			) as res:
				total_filesize = int(res.headers["Content-Length"])

				if not progress_handler:
					progress_handler = DefaultProgressHandler()

				progress_handler.initialize(
					None,
					title,
					quality_key,
					total_filesize,
					0,
					track_id=track["SNG_ID"],  # type: ignore
				)
				decrytor = DecryptDeezer(blowfish_key, progress_handler)
				await decrytor.output_file(total_filesize, download_path, res)

		if with_metadata:
			tags = await self.get_track_tags(track, separator=tag_separator)
			if ext.lower() == ".flac":
				self._write_flac_tags(download_path, track, tags=tags)
			else:
				self._write_mp3_tags(download_path, track, tags=tags)

		if with_lyrics:
			lyrics_path = path.join(download_dir, filename[: -len(ext)])
			self.save_lyrics(lyric_data, lyrics_path)  # type: ignore

		if show_messages:
			print("Track downloaded to:", download_path)

		progress_handler.close(track_id=track["SNG_ID"], size_downloaded=total_filesize)

	async def get_track_download_url(
		self, track, quality=None, fallback=True, renew=False, **kwargs
	):
		if renew:
			track = self.get_track(track["SNG_ID"])["info"]

		if not quality:
			quality = track_formats.MP3_128
			fallback = True

		try:
			# Just in case they passed in the whole dictionary from get_track()
			track = track["DATA"] if "DATA" in track else track

			if "MD5_ORIGIN" not in track:
				raise DownloadLinkDecryptionError("MD5 is needed to decrypt the download link.")

			md5_origin = track["MD5_ORIGIN"]
			track_id = track["SNG_ID"]
			media_version = track["MEDIA_VERSION"]
		except ValueError:
			raise ValueError(
				'You have passed an invalid argument. This method needs the "DATA" value in the dictionary returned by the get_track() method.'
			)

		def decrypt_url(quality_code):
			magic_char = "¤"
			step1 = magic_char.join((md5_origin, str(quality_code), track_id, media_version))
			m = hashlib.md5()
			m.update(bytes([ord(x) for x in step1]))

			step2 = m.hexdigest() + magic_char + step1 + magic_char
			step2 = step2.ljust(80, " ")

			cipher = Cipher(
				algorithms.AES(bytes("jo6aey6haid2Teih", "ascii")), modes.ECB(), default_backend()
			)

			encryptor = cipher.encryptor()
			step3 = encryptor.update(bytes([ord(x) for x in step2])).hex()

			cdn = track["MD5_ORIGIN"][0]

			return f"https://e-cdns-proxy-{cdn}.dzcdn.net/mobile/1/{step3}"

		url_try: list[str] = []
		url = decrypt_url(track_formats.TRACK_FORMAT_MAP[quality]["code"])

		cookies = self.get_cookies()
		async with aiohttp.ClientSession() as session:
			async with session.get(url, cookies=cookies) as res:
				if not fallback or (res.status == 200 and int(res.headers["Content-length"]) > 0):
					return (url, quality)
				url_try.append(url)
				if "fallback_qualities" in kwargs:
					fallback_qualities = kwargs["fallback_qualities"]
				else:
					fallback_qualities = track_formats.FALLBACK_QUALITIES

				for key in fallback_qualities:
					url = decrypt_url(track_formats.TRACK_FORMAT_MAP[key]["code"])

					async with session.get(url, cookies=cookies) as res2:
						if res2.status == 200 and int(res.headers["Content-length"]) > 0:
							return (url, key)
						url_try.append(url)

		raise DlDeezerNotUrlFoundException("Can't find valid URL to download '%s'. URLs try :\n- %s", track, "\n -".join(url_try))

	async def get_user_data(self):
		data = (await self._api_call(api_methods.GET_USER_DATA))["results"]

		self.token = data["checkForm"]

		if not data["USER"]["USER_ID"]:
			raise LoginError("Arl is invalid.")

		raw_user = data["USER"]

		cookies = self.get_cookies()
		if not cookies:
			raise ValueError("cookies is None")

		if raw_user["USER_PICTURE"]:
			self.user = {
				"id": raw_user["USER_ID"],
				"name": raw_user["BLOG_NAME"],
				"arl": cookies["arl"],
				"image": "https://e-cdns-images.dzcdn.net/images/user/{0}/250x250-000000-80-0-0.jpg".format(
					raw_user["USER_PICTURE"]
				),
			}
		else:
			self.user = {
				"id": raw_user["USER_ID"],
				"name": raw_user["BLOG_NAME"],
				"arl": cookies["arl"],
				"image": "https://e-cdns-images.dzcdn.net/images/user/250x250-000000-80-0-0.jpg",
			}

	async def _api_call(self, method, params={}):
		token = "null"
		if method != api_methods.GET_USER_DATA:
			if not self.token:
				await self.get_user_data()
			token = self.token

		async with aiohttp.ClientSession() as session:
			async with session.post(
				api_urls.API_URL,
				json=params,
				params={"api_version": "1.0", "api_token": token, "input": "3", "method": method},
				cookies=self.get_cookies(),
			) as res:
				data = await res.json()

				for key, morsel in res.cookies.items():
					self.set_cookie(key, morsel.value)

				if "error" in data and data["error"]:
					error_type = list(data["error"].keys())[0]
					error_message = data["error"][error_type]
					raise APIRequestError("{0} : {1}".format(error_type, error_message))

		return data

	async def get_track_tags(self, track, separator=", "):
		track = track["DATA"] if "DATA" in track else track

		album_data = await self.get_album(track["ALB_ID"])

		if "main_artist" in track["SNG_CONTRIBUTORS"]:
			main_artists = track["SNG_CONTRIBUTORS"]["main_artist"]
			artists = main_artists[0]
			for i in range(1, len(main_artists)):
				artists += separator + main_artists[i]
		else:
			artists = track["ART_NAME"]

		title = track["SNG_TITLE"]

		if "VERSION" in track and track["VERSION"] != "":
			title += " " + track["VERSION"]

		def should_include_featuring():
			# Checks if the track title already have the featuring artists in its title
			feat_keywords = ["feat.", "featuring", "ft."]

			for keyword in feat_keywords:
				if keyword in title.lower():
					return False
			return True

		if should_include_featuring() and "featuring" in track["SNG_CONTRIBUTORS"]:
			featuring_artists_data = track["SNG_CONTRIBUTORS"]["featuring"]
			featuring_artists = featuring_artists_data[0]
			for i in range(1, len(featuring_artists_data)):
				featuring_artists += separator + featuring_artists_data[i]

			title += f" (feat. {featuring_artists})"

		total_tracks = album_data["nb_tracks"]
		track_number = str(track["TRACK_NUMBER"]) + "/" + str(total_tracks)

		cover = self.get_album_poster(album_data, size=1000)

		tags = {
			"title": title,
			"artist": artists,
			"genre": None,
			"album": track["ALB_TITLE"],
			"albumartist": track["ART_NAME"],
			"label": album_data["label"],
			"date": track["PHYSICAL_RELEASE_DATE"],
			"discnumber": track["DISK_NUMBER"],
			"tracknumber": track_number,
			"isrc": track["ISRC"],
			"copyright": track["COPYRIGHT"],
			"_albumart": cover,
		}

		if len(album_data["genres"]["data"]) > 0:
			tags["genre"] = album_data["genres"]["data"][0]["name"]

		if "author" in track["SNG_CONTRIBUTORS"]:
			_authors = track["SNG_CONTRIBUTORS"]["author"]

			authors = _authors[0]
			for i in range(1, len(_authors)):
				authors += separator + _authors[i]

			tags["author"] = authors

		return tags

	async def get_track_info(self, track_id):
		method = api_methods.SONG_GET_DATA
		params = {"SNG_ID": track_id}

		if not int(track_id) < 0:
			method = api_methods.PAGE_TRACK

		data = await self._api_call(method, params=params)

		if "DATA" in data["results"]:
			return data["results"]["DATA"]
		return data["results"]

	async def get_album(self, album_id):
		data = await self._legacy_api_call("/album/{0}".format(album_id))

		# TODO: maybe better logic?
		data["cover_id"] = str(data["cover_small"]).split("cover/")[1].split("/")[0]

		return data

	async def _legacy_api_call(self, method, params={}):
		url = "{0}/{1}".format(api_urls.LEGACY_API_URL, method)
		async with aiohttp.ClientSession() as session:
			async with session.get(
				url,
				params=params,
				cookies=self.get_cookies(),
			) as res:
				data = await res.json()

				if "error" in data and data["error"]:
					error_type = data["error"]["type"]
					error_message = data["error"]["message"]
					error_code = data["error"]["code"]
					if error_code == 4:
						logging.warning("Download RateLimit '%s'", url)
						await asyncio.sleep(5)
						return await self._legacy_api_call(method, params)

					raise APIRequestError("{0} : {1}".format(error_type, error_message))

		return data
