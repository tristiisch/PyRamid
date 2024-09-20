import asyncio
import os
import traceback
from typing import Any

import pydeezer.util
from pyramid.api.services import IConfigurationService, ILoggerService
from pyramid.api.services.deezer_downloader import IDeezerDownloaderService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.deezer.downloader_progress_bar import DownloaderProgressBar
from pyramid.connector.deezer.py_deezer import PyDeezer
from pyramid.data.track import Track
from pyramid.tools.generate_token import DeezerTokenProvider, DeezerTokenEmptyException, DeezerTokenOverflowException
from pydeezer.constants import track_formats
from pydeezer.exceptions import LoginError
from urllib3.exceptions import MaxRetryError

from pyramid.data.exceptions import CustomException


@pyramid_service(interface=IDeezerDownloaderService)
class DeezerDownloaderService(IDeezerDownloaderService, ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			configuration_service: IConfigurationService
		):
		self.__logger = logger_service
		self.__configuration_service = configuration_service

	def start(self):
		# arl = self.__configuration_service.deezer__arl
		arl = None
		if arl is not None and arl != "":
			self.__deezer_dl_api = PyDeezer(arl)
			self.__token_provider = None
		else:
			self.__deezer_dl_api = None
			self.__token_provider = DeezerTokenProvider()
		self.music_format = track_formats.MP3_128
		os.makedirs(self.__configuration_service.deezer__folder, exist_ok=True)

	async def check_credentials(self) -> dict[str, Any]:
		if not self.__deezer_dl_api:
			raise Exception("deezer_dl_api not init")
		try:
			await self.__deezer_dl_api.get_user_data()
			return self.__deezer_dl_api.user
		except LoginError as err:
			raise err  # Arl is invalid

	async def dl_track_by_id(self, track_id) -> Track | None:
		client = await self._get_client()
		# try:
		track_info = await client.get_track_info(track_id)
		# except APIRequestError as err:
		# 	self.__logger.warn(f"Unable to download deezer song {track_id} : {err}", exc_info=True)
		# 	return None  # Track unvailable in this country

		if not track_info:
			self.__logger.error(f"Unable to find deezer song to download {track_id} : Unknown error")
			return None

		file_name = pydeezer.util.clean_filename(
			f"{track_info['ART_NAME']} - {track_info['SNG_TITLE']}"
		)
		file_path = os.path.join(self.__configuration_service.deezer__folder, file_name) + ".mp3"

		if os.path.exists(file_path) is False:
			is_dl = await self.__dl_track(track_info, file_name)
			if not is_dl:
				return None

		track_downloaded = Track(track_info, file_path)
		return track_downloaded

	async def __dl_track(self, track_info, file_name: str) -> bool:
		try:
			client = await self._get_client()
			await client.download_track(
				track_info,
				self.__configuration_service.deezer__folder,
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
			self.__logger.warning("Downloader MaxRetryError %s", track)
			await asyncio.sleep(5)
			return await self.__dl_track(track_info, file_name)

		except CustomException as error:
			trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
			self.__logger.warning("%s :\n%s", error.msg, trace)
			return False

		except Exception:
			track = Track(track_info, None)
			self.__logger.warning("Unable to dl track %s", track, exc_info=True)
			return False
	
	async def _get_client(self) -> PyDeezer:
		i = 0
		max_error = 10

		if self.__deezer_dl_api:
			return self.__deezer_dl_api
		if not self.__token_provider:
			raise Exception("token_provider not init")
		
		while True:
			try:
				token = self.__token_provider.next()
				self.__deezer_dl_api = PyDeezer(token.token)
				await self.check_credentials()
				break

			except DeezerTokenEmptyException as err:
				if i > max_error:
					raise err
				self.__token_provider = DeezerTokenProvider()

			except DeezerTokenOverflowException as err:
				if i > max_error:
					raise err
				self.__token_provider = DeezerTokenProvider()

			except LoginError as err:
				if i > max_error:
					raise err
			i += 1

		return self.__deezer_dl_api
