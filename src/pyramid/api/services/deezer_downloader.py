from abc import ABC, abstractmethod
from typing import Any
from pyramid.data.track import Track

class IDeezerDownloaderService(ABC):

	@abstractmethod
	async def check_credentials(self) -> dict[str, Any]:
		pass

	@abstractmethod
	async def dl_track_by_id(self, track_id) -> Track | None:
		pass
