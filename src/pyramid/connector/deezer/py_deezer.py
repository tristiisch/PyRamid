from os import path

import aiofiles
import aiohttp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydeezer import Deezer, util
from pydeezer.constants import track_formats, api_methods, api_urls, networking_settings
from pydeezer.exceptions import APIRequestError
from pydeezer.ProgressHandler import BaseProgressHandler, DefaultProgressHandler
from functools import partial
from pydeezer.exceptions import LoginError


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
		"""Downloads the given track

		Arguments:
		                                track {dict} -- Track dictionary, similar to the {info} value that is returned {using get_track()}
		                                download_dir {str} -- Directory (without {filename}) where the file is to be saved.

		Keyword Arguments:
		                                quality {str} -- Use values from {constants.track_formats}, will get the default quality if None or an invalid is given. (default: {None})
		                                filename {str} -- Filename with or without the extension (default: {None})
		                                renew {bool} -- Will renew the track object (default: {False})
		                                with_metadata {bool} -- If true, will write id3 tags into the file. (default: {True})
		                                with_lyrics {bool} -- If true, will find and save lyrics of the given track. (default: {True})
		                                tag_separator {str} -- Separator to separate multiple artists (default: {", "})
		"""

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

		tags = self.get_track_tags(track, separator=tag_separator)

		res = self.get_track_download_url(track, quality, fallback=fallback, renew=renew, **kwargs)
		if res is None:
			raise Exception()
		url, quality_key = res

		blowfish_key = util.get_blowfish_key(track["SNG_ID"])

		# quality = self._select_valid_quality(track, quality)

		quality = track_formats.TRACK_FORMAT_MAP[quality_key]

		title = tags["title"]
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
		## ----

		async with aiohttp.ClientSession() as session:
			async with session.get(
				url,
				cookies=self.get_cookies(),
				timeout=None,
				headers=networking_settings.HTTP_HEADERS,
				chunked=True,
				ssl=None,
			) as res:
				chunk_size = 2048
				total_filesize = int(res.headers["Content-Length"])
				i = 0

				data_iter = res.content.iter_chunked(2048)

				if not progress_handler:
					progress_handler = DefaultProgressHandler()

				progress_handler.initialize(
					data_iter,
					title,
					quality_key,
					total_filesize,
					chunk_size,
					track_id=track["SNG_ID"],  # type: ignore
				)

				async with aiofiles.open(download_path, "wb") as f:
					await f.seek(0)

					async for chunk in data_iter:
						current_chunk_size = len(chunk)

						if i % 3 > 0:
							await f.write(chunk)
						elif len(chunk) < chunk_size:
							await f.write(chunk)
							progress_handler.update(
								track_id=track["SNG_ID"], current_chunk_size=current_chunk_size
							)
							break
						else:
							cipher = Cipher(
								algorithms.Blowfish(blowfish_key),
								modes.CBC(bytes([i for i in range(8)])),
								default_backend(),
							)

							decryptor = cipher.decryptor()
							dec_data = decryptor.update(chunk) + decryptor.finalize()
							await f.write(dec_data)

							current_chunk_size = len(dec_data)

						i += 1

						progress_handler.update(
							track_id=track["SNG_ID"], current_chunk_size=current_chunk_size
						)

		if with_metadata:
			if ext.lower() == ".flac":
				self._write_flac_tags(download_path, track, tags=tags)
			else:
				self._write_mp3_tags(download_path, track, tags=tags)

		if with_lyrics:
			lyrics_path = path.join(download_dir, filename[: -len(ext)])
			self.save_lyrics(lyric_data, lyrics_path)  # type: ignore

		if show_messages:
			print("Track downloaded to:", download_path)

		progress_handler.close(track_id=track["SNG_ID"], total_filesize=total_filesize)

	async def get_user_data(self):
		"""Gets the data of the user, this will only work arl is the cookie. Make sure you have run login_via_arl() before using this.

		Raises:
		        LoginError: Will raise if the arl given is not identified by Deezer
		"""

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

	async def get_track(self, track_id):
		"""Gets the track info using the Deezer API

		Arguments:
		        track_id {str} -- Track Id

		Returns:
		        dict -- Dictionary that contains the {info}, {download} partial function, {tags}, and {get_tag} partial function.
		"""

		method = api_methods.SONG_GET_DATA
		params = {"SNG_ID": track_id}

		if not int(track_id) < 0:
			method = api_methods.PAGE_TRACK

		data = await self._api_call(method, params=params)
		data = data["results"]

		return {
			"info": data,
			"download": partial(self.download_track, data),
			"tags": self.get_track_tags(data),
			"get_tag": partial(self.get_track_tags, data),
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
