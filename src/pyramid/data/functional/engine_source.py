from typing import Dict
from connector.deezer.downloader import DeezerDownloader
from connector.deezer.search import DeezerSearch
from connector.spotify.search import SpotifySearch
from data.a_search import ASearch
from data.track import Track, TrackMinimal, TrackMinimalDeezer
from tools.configuration import Configuration


class EngineSource:
	def __init__(self, config: Configuration):
		self.__downloader = DeezerDownloader(config.deezer_arl, config.deezer_folder)
		self.__deezer_search = DeezerSearch(config.default_limit_track)
		self.__spotify_search = SpotifySearch(
			config.default_limit_track, config.spotify_client_id, config.spotify_client_secret
		)
		self.default_engine: ASearch = self.__deezer_search
		self.__downloader_search = self.__deezer_search
		self.__search_engines: Dict[str, ASearch] = dict(
			{
				"spotify": self.__spotify_search,
				"deezer": self.__deezer_search,
			}
		)

	async def download_track(self, track: TrackMinimal) -> Track | None:
		track_used: TrackMinimalDeezer

		if not isinstance(track, TrackMinimalDeezer):
			t = self.__downloader_search.search_exact_track(track.author_name, None, track.name)
			if t is None:
				return None
			track_used = t
		else:
			track_used = track

		return await self.__downloader.dl_track_by_id(track_used.id)

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

	def get_engine(self, name: str):
		return self.__search_engines.get(name.lower())
