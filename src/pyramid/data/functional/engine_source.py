from enum import Enum
from typing import Dict

from pyramid.connector.deezer.downloader import DeezerDownloader
from pyramid.connector.deezer.search import DeezerSearch
from pyramid.connector.spotify.search import SpotifySearch
from pyramid.data.a_search import ASearch
from pyramid.data.exceptions import EngineSourceNotFoundException, TrackNotFoundException
from pyramid.data.track import Track, TrackMinimal, TrackMinimalDeezer
from pyramid.tools.configuration.configuration import Configuration


class SourceType(Enum):
	Spotify = 1
	Deezer = 2


class EngineSource:
	def __init__(self, config: Configuration):
		# self.__downloader = DeezerDownloader(config.deezer__folder, config.deezer__arl)
		self.__downloader = DeezerDownloader(config.deezer__folder)
		self.__deezer_search = DeezerSearch(config.general__limit_tracks)
		self.__spotify_search = SpotifySearch(
			config.general__limit_tracks, config.spotify__client_id, config.spotify__client_secret
		)
		self.__default_source: ASearch = self.__deezer_search
		self.__downloader_source = self.__deezer_search
		self.__sources: Dict[SourceType, ASearch] = dict(
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
		for engine in self.__sources.values():
			result = await engine.get_by_url(url)
			if result:
				break

		if not result:
			raise TrackNotFoundException("URL **%s** not found.", url)

		if isinstance(result, tuple):
			tracks, tracks_unfindable = result
			if not all(isinstance(t, TrackMinimalDeezer) for t in tracks):
				tracks = await self._equivalents_for_download(tracks, tracks_unfindable)
			return tracks, tracks_unfindable

		elif not isinstance(result, TrackMinimalDeezer):
			return await self._equivalent_for_download(result)

		raise ValueError("The type of result 'get_by_url' is unknown.")

	async def search_track(self, input: str, engine: SourceType | None) -> TrackMinimalDeezer:
		search_engine = self._resolve_engine(engine)
		search_engine_name = self._get_engine_name(search_engine)

		track: TrackMinimal | None = await search_engine.search_track(input)
		if not track:
			raise TrackNotFoundException(
				"Search **%s** not found on %s.", input, search_engine_name
			)

		if not isinstance(track, TrackMinimalDeezer):
			return await self._equivalent_for_download(track)
		return track

	async def search_tracks(
		self, input: str, engine: SourceType | None, limit: int | None = None
	) -> tuple[list[TrackMinimal], list[TrackMinimal]]:
		search_engine = self._resolve_engine(engine)
		search_engine_name = self._get_engine_name(search_engine)

		tracks = await search_engine.search_tracks(input, limit)
		if not tracks:
			raise TrackNotFoundException(
				"Search **%s** not found on %s.", input, search_engine_name
			)
		tracks_unfindable: list[TrackMinimal] = []

		if not all(isinstance(t, TrackMinimalDeezer) for t in tracks):
			tracks = await self._equivalents_for_download(tracks, tracks_unfindable)
		return tracks, tracks_unfindable  # type: ignore

	def _get_engine(self, engine: SourceType):
		return self.__sources.get(engine)

	def _get_engine_name(self, engine: ASearch):
		for key, value in self.__sources.items():
			if value == engine:
				return key.name
		return None

	def _resolve_engine(self, engine: SourceType | None):
		if engine is None:
			return self.__default_source

		custom_engine = self._get_engine(engine)
		if not custom_engine:
			raise EngineSourceNotFoundException("Search engine **%s** not found.", engine.name)
		return custom_engine

	async def _equivalent_for_download(self, track: TrackMinimal) -> TrackMinimalDeezer:
		track_exact_equiv = await self._equivalent_for_download_isrc(track)
		if track_exact_equiv:
			if track_exact_equiv.available:
				return track_exact_equiv
			else:
				track = track_exact_equiv

		track_search_equiv = await self._equivalent_for_download_str(track)
		if not track_search_equiv:
			if track_exact_equiv:
				return track_exact_equiv
			dl_engine_name = self._get_engine_name(self.__downloader_source)
			raise TrackNotFoundException(
				"Track **%s** has not been found on %s.", track, dl_engine_name
			)
			## TODO SAVE THIS
		return track_search_equiv

	async def _equivalent_for_download_str(self, track: TrackMinimal) -> TrackMinimalDeezer | None:
		track_dl_search = await self.__downloader_source.search_exact_track(
			track.author_name, track.album_title, track.name
		)
		return track_dl_search

	async def _equivalent_for_download_isrc(self, track: TrackMinimal) -> TrackMinimalDeezer | None:
		if not hasattr(track, "isrc") or track.isrc is None:  # type: ignore
			return None
		track_dl_search = await self.__downloader_source.get_track_by_isrc(
			track.isrc  # type: ignore
		)
		return track_dl_search

	async def _equivalents_for_download(
		self, tracks: list[TrackMinimal], tracks_unfindable: list[TrackMinimal]
	) -> list[TrackMinimalDeezer]:
		tracks_downloadable: list[TrackMinimalDeezer] = [] * len(tracks)

		for t in tracks:
			try:
				if isinstance(t, TrackMinimalDeezer):
					tracks_downloadable.append(t)
				else:
					track_dl_search = await self._equivalent_for_download(t)
					if track_dl_search.available is False:
						tracks_unfindable.append(t)
					else:
						tracks_downloadable.append(track_dl_search)

			except TrackNotFoundException:
				tracks_unfindable.append(t)
		return tracks_downloadable
