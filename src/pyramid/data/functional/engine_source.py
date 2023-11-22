from enum import Enum
from typing import Dict
from connector.deezer.downloader import DeezerDownloader
from connector.deezer.search import DeezerSearch
from connector.spotify.search import SpotifySearch
from data.a_search import ASearch
from data.track import Track, TrackMinimal, TrackMinimalDeezer
from connector.database.obj.track import TrackStored
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
		self.__downloader_search = self.__deezer_search
		self.__search_engines: Dict[SourceType, ASearch] = dict(
			{
				SourceType.Spotify: self.__spotify_search,
				SourceType.Deezer: self.__deezer_search,
			}
		)
		self.__default_engine: ASearch = self.__search_engines[SourceType.Deezer]

	async def download_track(self, track: TrackMinimal) -> Track | None:
		track_used: TrackMinimalDeezer

		if not isinstance(track, TrackMinimalDeezer):
			t = self.__downloader_search.search_exact_track(track.author_name, None, track.name)
			if t is None:
				return None
			track_used = t
		else:
			track_used = track

		track_stored = TrackStored(
			dl_id=track_used.id, name=track_used.name, artist=track_used.author_name, album=track_used.album_title
		)
		TrackStored.add_if_not_exists(track_stored, False)
		return await self.__downloader.dl_track_by_id(track_used.id)
	
	def search_track(self, track_identifier: str, source: SourceType | None = None):
		if source:
			engine = self.__search_engines.get(source)
			if not engine:
				return None # TODO "Search engine **{source.name}** not found."
		else:
			engine = self.__default_engine

		track: TrackMinimal | None = engine.search_track(track_identifier)

		return track
	
	def search_tracks(self, track_identifier: str, source: SourceType | None = None):
		if source:
			engine = self.__search_engines.get(source)
			if not engine:
				return None # TODO "Search engine **{source.name}** not found."
		else:
			engine = self.__default_engine

		tracks: list[TrackMinimal] | None = engine.search_tracks(track_identifier)

		return tracks

	async def search_by_url(self, url: str):
		"""
		Search for tracks by URL using multiple search engines.

		:param url: The URL to search for.
		"""
		for engine in self.__search_engines.values():
			result = await engine.get_by_url(url)
			if result is not None:
				return result

		return None
