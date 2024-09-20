from abc import abstractmethod
from pyramid.data.a_search import ASearch
from pyramid.data.track import TrackMinimalSpotify


class ISpotifySearchService(ASearch):

	@abstractmethod
	async def search_tracks(
		self, search, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		pass

	@abstractmethod
	async def search_track(self, search) -> TrackMinimalSpotify | None:
		pass

	@abstractmethod
	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalSpotify] | None:
		pass

	@abstractmethod
	async def get_album_tracks(self, album_name) -> list[TrackMinimalSpotify] | None:
		pass

	async def get_top_artist(
		self, artist_name, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		pass

	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | TrackMinimalSpotify | None:
		pass