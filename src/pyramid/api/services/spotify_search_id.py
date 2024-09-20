from abc import abstractmethod

from pyramid.data.a_search import ASearchId
from pyramid.data.track import TrackMinimalSpotify

class ISpotifySearchIdService(ASearchId):

	@abstractmethod
	async def get_track_by_id(self, track_id: str) -> TrackMinimalSpotify | None:
		pass

	@abstractmethod
	async def get_playlist_tracks_by_id(
		self, playlist_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		pass

	@abstractmethod
	async def get_album_tracks_by_id(
		self, album_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		pass

	@abstractmethod
	async def get_top_artist_by_id(
		self, artist_id: str, limit: int | None = None
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		pass
