from abc import abstractmethod
from typing import Any

class ISpotifyClientService:

	@abstractmethod
	async def async_search(self, q, limit=10, offset=0, type="track", market=None) -> dict[str, Any]:
		pass

	@abstractmethod
	async def async_track(self, track_id, market=None)  -> dict[str, Any]:
		pass

	@abstractmethod
	async def async_playlist_items(
		self,
		playlist_id,
		fields=None,
		limit=100,
		offset=0,
		market=None,
		additional_types=("track", "episode"),
	)  -> dict[str, Any]:
		pass

	@abstractmethod
	async def async_album_tracks(self, album_id, limit=50, offset=0, market=None) -> dict[str, Any]:
		pass

	@abstractmethod
	async def async_artist_top_tracks(self, artist_id, country="US") -> dict[str, Any]:
		pass

	@abstractmethod
	async def async_next(self, result) -> dict[str, Any] | None:
		pass
