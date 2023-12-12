import asyncio
import json
import logging
import os

import pydeezer.util
from connector.deezer.downloader_progress_bar import DownloaderProgressBar
from connector.deezer.py_deezer import PyDeezer
from data.track import Track, TrackMinimalDeezer
from pydeezer.constants import track_formats
from pydeezer.exceptions import LoginError
from urllib3.exceptions import MaxRetryError


class DeezerDownloader:
	def __init__(self, arl, folder):
		self.__deezer_dl_api = PyDeezer(arl)
		self.folder_path = folder
		self.music_format = track_formats.MP3_128

	async def check_credentials(self):
		try:
			await self.__deezer_dl_api.get_user_data()
			return self.__deezer_dl_api.user
		except LoginError as err:
			raise err  # Arl is invalid

	async def dl_track_by_id(self, track_id) -> Track | None:
		# try:
		track_info = await self.__deezer_dl_api.get_track_info(track_id)
		# except APIRequestError as err:
		# 	logging.warn(f"Unable to download deezer song {track_id} : {err}", exc_info=True)
		# 	return None  # Track unvailable in this country

		if not track_info:
			logging.error(f"Unable to find deezer song to download {track_id} : Unknown error")
			return None

		file_name = pydeezer.util.clean_filename(
			f"{track_info['ART_NAME']} - {track_info['SNG_TITLE']}"
		)
		file_path = os.path.join(self.folder_path, file_name) + ".mp3"

		if os.path.exists(file_path) is False:
			is_dl = await self.__dl_track(track_info, file_name)
			if not is_dl:
				return None

		track_downloaded = Track(track_info, file_path)
		return track_downloaded

	async def __dl_track(self, track_info, file_name: str) -> bool:
		try:
			await self.__deezer_dl_api.download_track(
				track_info,
				self.folder_path,
				self.music_format,
				True,  # fallback quality if not available
				file_name,
				False,  # renew track info
				False,  # metadata
				False,  # lyrics
				", ",  # separator for multiple artists
				False,  # show messages
				DownloaderProgressBar(),  # Custom progress bar
			)
			return True
		except MaxRetryError:
			track = Track(track_info, None)
			logging.warning("Downloader MaxRetryError %s", track)
			await asyncio.sleep(5)
			return await self.__dl_track(track_info, file_name)
		except Exception:
			track = Track(track_info, None)
			logging.warning("Unable to dl track %s", track, exc_info=True)
			return False
