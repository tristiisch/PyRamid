import asyncio
import logging
import os
import traceback
from typing import Any

import pydeezer.util
from pyramid.api.services import IConfigurationService, ILoggerService
from pyramid.api.services.deezer_downloader import IDeezerDownloaderService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.deezer.downloader_progress_bar import DownloaderProgressBar
from pyramid.connector.deezer.download.client import PyDeezer
from pyramid.data.music.track import Track
from pyramid.tools.generate_token import DeezerTokenProvider
from pydeezer.constants import track_formats
from pydeezer.exceptions import LoginError
from urllib3.exceptions import MaxRetryError

from pyramid.data.exceptions import CustomException, DeezerTokenInvalidException, DeezerTokenOverflowException, DeezerTokensUnavailableException


@pyramid_service(interface=IDeezerDownloaderService)
class DeezerDownloaderService(IDeezerDownloaderService, ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			configuration_service: IConfigurationService
		):
		self.__logger = logger_service
		self.__configuration_service = configuration_service

	def start(self):
		arl = self.__configuration_service.deezer__arl
		if arl is not None and arl != "":
			self.__arls = [arl]
		else:
			self.__arls = None
		self.__token_provider = DeezerTokenProvider()
		self.music_format = track_formats.MP3_128

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
			self.__logger.warning("%s :\n%s", error.args, trace)
			return False

		except Exception:
			track = Track(track_info, None)
			self.__logger.warning("Unable to dl track %s", track, exc_info=True)
			return False
	
	async def _get_client(self) -> PyDeezer:
		return await self._define_client()
	
	async def _define_client(self) -> PyDeezer:
		last_err_local = None
		if self.__arls:
			for arl in self.__arls:
				deezer_dl_api = PyDeezer(arl)
				try:
					await deezer_dl_api.get_user_data()
					return deezer_dl_api
				except DeezerTokenInvalidException as err:
					last_err_local = err
					continue

		last_err_remote = None
		already_overflow = False
		while self.__token_provider.count_valids_tokens() != 0:
			try:
				token = self.__token_provider.next()
				deezer_dl_api = PyDeezer(token.token)
				await deezer_dl_api.get_user_data()
				return deezer_dl_api

			except DeezerTokenInvalidException as err:
				last_err_remote = err
				continue

			except DeezerTokenOverflowException as err:
				last_err_remote = err
				if already_overflow is True:
					break
				already_overflow = True
				self.__token_provider = DeezerTokenProvider()
				continue

			except DeezerTokensUnavailableException as err:
				last_err_remote = err
				break

		if last_err_local is not None:
			tb = traceback.TracebackException.from_exception(last_err_local)
			formatted_tb = ''.join(tb.format())
			logging.warning("Failed to fetch valid Deezer client from local\n%s", formatted_tb)

		if last_err_remote is not None:
			tb = traceback.TracebackException.from_exception(last_err_remote)
			formatted_tb = ''.join(tb.format())
			logging.warning("Failed to fetch valid Deezer client from remote\n%s", formatted_tb)

		if last_err_remote is not None and last_err_local is not None:
			raise last_err_remote
		raise Exception("Unknown func exit")
