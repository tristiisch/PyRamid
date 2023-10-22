import abc

from abc import ABC
from tools.object import TrackMinimal


class ASearch(ABC):
	@abc.abstractmethod
	def search_track(self, search) -> TrackMinimal | None:
		pass

	@abc.abstractmethod
	def search_tracks(self, search, limit=10) -> list[TrackMinimal] | None:
		pass
