

from abc import ABC, abstractmethod
from pyramid.data.a_search import ASearch
from pyramid.data.music.track_minimal_deezer import TrackMinimalDeezer


class IDeezerSearchService(ASearch):

	@abstractmethod
	async def search_track(self, search) -> TrackMinimalDeezer | None:
		pass

	@abstractmethod
	async def get_track_by_id(self, track_id: int) -> TrackMinimalDeezer | None:
		pass

	@abstractmethod
	async def get_track_by_isrc(self, isrc: str) -> TrackMinimalDeezer | None:
		pass

	@abstractmethod
	async def search_tracks(
		self, search, limit: int | None = None
	) -> list[TrackMinimalDeezer] | None:
		pass

	@abstractmethod
	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalDeezer] | None:
		pass

	@abstractmethod
	async def get_playlist_tracks_by_id(
		self, playlist_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		pass

	@abstractmethod
	async def get_album_tracks(self, album_name) -> list[TrackMinimalDeezer] | None:
		pass

	@abstractmethod
	async def get_album_tracks_by_id(
		self, album_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		pass

	@abstractmethod
	async def get_top_artist(
		self, artist_name, limit: int | None = None
	) -> list[TrackMinimalDeezer] | None:
		pass

	@abstractmethod
	async def get_top_artist_by_id(
		self, artist_id: int, limit: int | None = None
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		pass

	@abstractmethod
	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | TrackMinimalDeezer | None:
		pass

	@abstractmethod
	async def search_exact_track(
		self, artist_name, album_title, track_title
	) -> TrackMinimalDeezer | None:
		pass
