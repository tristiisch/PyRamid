from abc import ABC, abstractmethod

from tools.object import TrackMinimal

class ASearch(ABC):
	@abstractmethod
	def search_track(self, search) -> TrackMinimal | None:
		pass

	@abstractmethod
	def search_tracks(self, search, limit = 10) -> list[TrackMinimal] | None:
		pass
