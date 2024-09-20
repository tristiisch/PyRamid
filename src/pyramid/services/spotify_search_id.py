from typing import Any

from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.spotify_client import ISpotifyClientService
from pyramid.api.services.spotify_search_base import ISpotifySearchBaseService
from pyramid.api.services.spotify_search_id import ISpotifySearchIdService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.data.track import TrackMinimalSpotify

@pyramid_service(interface=ISpotifySearchIdService)
class SpotifySearchIdService(ISpotifySearchIdService, ServiceInjector):

	def injectService(self,
			configuration_service: IConfigurationService,
			spotify_client: ISpotifyClientService,
			spotify_search_base: ISpotifySearchBaseService
		):
		self.__configuration_service = configuration_service
		self.__spotify_client = spotify_client
		self.__spotify_search_base = spotify_search_base

	async def get_track_by_id(self, track_id: str) -> TrackMinimalSpotify | None:
		result = await self.__spotify_client.async_track(track_id=track_id)
		if not result:
			return None
		return TrackMinimalSpotify(result)

	async def get_playlist_tracks_by_id(
		self, playlist_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks_playlist = await self.__spotify_search_base.items(
			await self.__spotify_client.async_playlist_items(playlist_id=playlist_id)
		)
		if not tracks_playlist:
			return None
		return [TrackMinimalSpotify(element["track"]) for element in tracks_playlist], []

	async def get_album_tracks_by_id(
		self, album_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks = await self.__spotify_search_base.items(
			await self.__spotify_client.async_album_tracks(album_id=album_id)
		)
		if not tracks:
			return None

		readable_tracks = []
		unreadable_tracks = []
		for t in tracks:
			track = await self.get_track_by_id(t["id"])
			if track is None:
				unreadable_tracks.append(t)
			else:
				readable_tracks.append(track)
		return readable_tracks, unreadable_tracks

	async def get_top_artist_by_id(
		self, artist_id: str, limit: int | None = None
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		if limit is None:
			limit = self.__configuration_service.general__limit_tracks
		results = await self.__spotify_client.async_artist_top_tracks(artist_id)

		if not results or not results.get("tracks"):
			return None

		tracks = results["tracks"]
		if len(tracks) > limit:
			tracks = tracks[:limit]
		return [TrackMinimalSpotify(element) for element in tracks], []