import abc

from abc import ABC
from track.track import TrackMinimal


class ASearch(ABC):
	@abc.abstractmethod
	def search_track(self, search) -> TrackMinimal | None:
		pass

	@abc.abstractmethod
	def search_tracks(self, search, limit=10) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	def get_playlist_tracks(self, playlist_name) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	def get_album_tracks(self, album_name) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	def get_top_artist(self, artist_name, limit=10) -> list[TrackMinimal] | None:
		pass

	@abc.abstractmethod
	async def get_by_url(self, url) -> tuple[list[TrackMinimal], list[TrackMinimal]] | TrackMinimal | None:
		pass
