from abc import ABC, abstractmethod
from pyramid.connector.deezer.download.client import PyDeezer
from pyramid.data.music.track import Track

class IDeezerDownloaderService(ABC):

	@abstractmethod
	async def dl_track_by_id(self, track_id) -> Track | None:
		pass

	@abstractmethod
	async def get_client(self) -> PyDeezer:
		pass
