from abc import ABC, abstractmethod
from pyramid.data.source_type import SourceType
from pyramid.data.music.track import Track
from pyramid.data.music.track_minimal_deezer import TrackMinimalDeezer
from pyramid.data.music.track_minimal import TrackMinimal

class ISourceService(ABC):

	@abstractmethod
	async def download_track(self, track: TrackMinimal) -> Track | None:
		pass

	@abstractmethod
	async def search_by_url(self, url: str) -> (tuple[list[TrackMinimalDeezer] | list[TrackMinimal], list[TrackMinimal]] | TrackMinimalDeezer):
		pass

	@abstractmethod
	async def search_track(self, input: str, engine: SourceType | None) -> TrackMinimalDeezer:
		pass

	@abstractmethod
	async def search_tracks(
		self, input: str, engine: SourceType | None, limit: int | None = None
	) -> tuple[list[TrackMinimal], list[TrackMinimal]]:
		pass