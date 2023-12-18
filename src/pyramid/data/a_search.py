import abc
from abc import ABC

from data.track import TrackMinimal


class ASearch(ABC):
	@abc.abstractmethod
	async def search_track(self, search) -> TrackMinimal | None:
		pass

	@abc.abstractmethod
	async def search_tracks(self, search, limit: int | None = None) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	async def get_album_tracks(self, album_name) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	async def get_top_artist(self, artist_name, limit=10) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimal], list[TrackMinimal]] | TrackMinimal | None:
		pass


class ASearchId(ABC):
	@abc.abstractmethod
	async def get_track_by_id(self, track_id: int | str) -> TrackMinimal | None:
		pass

	@abc.abstractmethod
	async def get_playlist_tracks_by_id(
		self, playlist_id: int | str
	) -> tuple[list[TrackMinimal], list[TrackMinimal]] | None:
		pass

	@abc.abstractmethod
	async def get_album_tracks_by_id(
		self, album_id: int | str
	) -> tuple[list[TrackMinimal], list[TrackMinimal]] | None:
		pass

	@abc.abstractmethod
	async def get_top_artist_by_id(
		self, artist_id: int | str, limit: int | None = None
	) -> tuple[list[TrackMinimal], list[TrackMinimal]] | None:
		pass
