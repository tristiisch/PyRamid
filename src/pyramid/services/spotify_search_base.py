


from typing import Any
from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.spotify_client import ISpotifyClientService
from pyramid.api.services.spotify_search_base import ISpotifySearchBaseService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector

@pyramid_service(interface=ISpotifySearchBaseService)
class SpotifySearchBaseService(ISpotifySearchBaseService, ServiceInjector):

	def injectService(self,
			configuration_service: IConfigurationService,
			spotify_client: ISpotifyClientService,
		):
		self.__configuration_service = configuration_service
		self.__spotify_client = spotify_client

	async def items(
		self,
		results: dict[str, Any],
		item_name="items"
	) -> list[dict[str, Any]] | None:
		if not results:
			return None
		tracks: list = results[item_name]

		while results["next"]:
			results = await self.__spotify_client.async_next(results)  # type: ignore
			tracks.extend(results[item_name])

		return tracks

	async def items_max(
		self,
		results: dict[str, Any],
		limit: int | None = None,
		item_name="items"
	) -> list[Any] | None:
		if not results or not results.get("tracks") or not results["tracks"].get(item_name):
			return None

		if limit is None:
			limit = self.__configuration_service.general__limit_tracks
		tracks: list[Any] = results["tracks"][item_name]

		results_tracks: dict[str, Any] = results["tracks"]
		while results["tracks"]["next"] and limit > len(tracks):
			results = await self.__spotify_client.async_next(results_tracks)  # type: ignore
			tracks.extend(results_tracks[item_name])

		if len(tracks) > limit:
			return tracks[:limit]

		return tracks
