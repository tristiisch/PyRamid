from enum import Enum
from typing import Dict

from connector.deezer.downloader import DeezerDownloader
from connector.deezer.search import DeezerSearch
from connector.spotify.search import SpotifySearch
from data.a_search import ASearch
from data.exceptions import EngineSourceNotFoundException, TrackNotFoundException
from data.track import Track, TrackMinimal, TrackMinimalDeezer
from tools.configuration.configuration import Configuration


class SourceType(Enum):
	Spotify = 1
	Deezer = 2


class EngineSource:
	def __init__(self, config: Configuration):
		self.__downloader = DeezerDownloader(config.deezer__arl, config.deezer__folder)
		self.__deezer_search = DeezerSearch(config.general__limit_tracks)
		self.__spotify_search = SpotifySearch(
			config.general__limit_tracks, config.spotify__client_id, config.spotify__client_secret
		)
		self.default_engine: ASearch = self.__deezer_search
		self.__downloader_search = self.__deezer_search
		self.__search_engines: Dict[SourceType, ASearch] = dict(
			{
				SourceType.Spotify: self.__spotify_search,
				SourceType.Deezer: self.__deezer_search,
			}
		)

	async def download_track(self, track: TrackMinimal) -> Track | None:
		track_used: TrackMinimalDeezer

		if not isinstance(track, TrackMinimalDeezer):
			# t = await self.__downloader_search.search_exact_track(track.author_name, None, track.name)
			# if t is None:
			# 	return None
			# track_used = t
			raise Exception("Unsupported operation")
		else:
			track_used = track

		return await self.__downloader.dl_track_by_id(track_used.id)

	async def search_by_url(self, url: str):
		"""
		Search for tracks by URL using multiple search engines.

		:param url: The URL to search for.
		"""
		result = None
		for engine in self.__search_engines.values():
			result = await engine.get_by_url(url)
			if result:
				break

		if not result:
			raise TrackNotFoundException(
				"URL **%s** not found.", url
			)
		if isinstance(result, tuple):
			tracks, tracks_unfindable = result
			if not all(isinstance(t, TrackMinimalDeezer) for t in tracks):
				tracks_downloadable = [] * len(tracks)

				for t in tracks:
					track_dl_search = await self.__downloader_search.search_exact_track(
						t.author_name, None, t.name
					)
					if not track_dl_search:
						tracks_unfindable.append(t)
						## TODO SAVE THIS
					else:
						tracks_downloadable.append(track_dl_search)
				return tracks_downloadable, tracks_unfindable
		elif not isinstance(result, TrackMinimalDeezer):
			track_dl_search = await self.__downloader_search.search_exact_track(
				result.author_name, None, result.name
			)
			if not track_dl_search:
				dl_engine_name = self.get_engine_name(self.__downloader_search)
				raise TrackNotFoundException(
					"Track **%s** has not been found on %s.", result, dl_engine_name
				)
				## TODO SAVE THIS
			result = track_dl_search

		return result

	async def search_track(self, input: str, engine: SourceType | None):
		if engine is None:
			search_engine = self.default_engine
		else:
			test_value = self.get_engine(engine)
			if not test_value:
				raise EngineSourceNotFoundException("Search engine **%s** not found.", engine)
			else:
				search_engine = test_value
		search_engine_name = self.get_engine_name(search_engine)

		track: TrackMinimal | None = search_engine.search_track(input)
		if not track:
			raise TrackNotFoundException(
				"Search **%s** not found on %s.", input, search_engine_name
			)

		if not isinstance(track, TrackMinimalDeezer):
			track_dl_search = await self.__downloader_search.search_exact_track(
				track.author_name, None, track.name
			)
			if not track_dl_search:
				dl_engine_name = self.get_engine_name(self.__downloader_search)
				raise TrackNotFoundException(
					"Track **%s** has not been found on %s.", track, dl_engine_name
				)
				## TODO SAVE THIS
			track = track_dl_search
		return track

	def get_engine(self, engine: SourceType):
		return self.__search_engines.get(engine)

	def get_engine_name(self, engine: ASearch):
		for key, value in self.__search_engines.items():
			if value == engine:
				return key
		return None
