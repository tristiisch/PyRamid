import re
from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.spotify_client import ISpotifyClientService
from pyramid.api.services.spotify_search import ISpotifySearchService
from pyramid.api.services.spotify_search_base import ISpotifySearchBaseService
from pyramid.api.services.spotify_search_id import ISpotifySearchIdService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.spotify.spotify_type import SpotifyType
from pyramid.data.exceptions import DiscordMessageException, RessourceBadFormatException, RessourceNotExistsException
from pyramid.data.music.track_minimal_spotify import TrackMinimalSpotify
from spotipy.exceptions import SpotifyException


@pyramid_service(interface=ISpotifySearchService)
class SpotifySearchService(ISpotifySearchService, ServiceInjector):

	def injectService(self,
			configuration_service: IConfigurationService,
			spotify_client: ISpotifyClientService,
			spotify_search_base: ISpotifySearchBaseService,
			spotify_search_id: ISpotifySearchIdService
		):
		self.__configuration_service = configuration_service
		self.__spotify_client = spotify_client
		self.__spotify_search_base = spotify_search_base
		self.__spotify_search_id = spotify_search_id

	async def search_tracks(
		self, search, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		if limit is None:
			limit = self.__configuration_service.general__limit_tracks
		if limit > 50:
			req_limit = 50
		else:
			req_limit = limit
		results = await self.__spotify_client.async_search(q=search, limit=req_limit, type="track")
		tracks = await self.__spotify_search_base.items_max(results, limit)
		if not tracks:
			return None
		return [TrackMinimalSpotify(element) for element in tracks]

	async def search_track(self, search) -> TrackMinimalSpotify | None:
		results = await self.__spotify_client.async_search(q=search, limit=1, type="track")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		track = tracks[0]

		return TrackMinimalSpotify(track)

	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalSpotify] | None:
		results = await self.__spotify_client.async_search(q=playlist_name, limit=1, type="playlist")

		if not results or not results.get("playlists") or not results["playlists"].get("items"):
			return None

		playlist_id = results["playlists"]["items"][0]["id"]
		tracks = await self.__spotify_search_id.get_playlist_tracks_by_id(playlist_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_album_tracks(self, album_name) -> list[TrackMinimalSpotify] | None:
		results = await self.__spotify_client.async_search(q=album_name, limit=1, type="album")

		if not results or not results.get("albums") or not results["albums"].get("items"):
			return None

		album_id = results["albums"]["items"][0]["id"]
		tracks = await self.__spotify_search_id.get_album_tracks_by_id(album_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_top_artist(
		self, artist_name, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		results = await self.__spotify_client.async_search(q=artist_name, limit=1, type="artist")

		if not results or not results.get("artists") or not results["artists"].get("items"):
			return None

		artist_id = results["artists"]["items"][0]["id"]
		tracks = await self.__spotify_search_id.get_top_artist_by_id(artist_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | TrackMinimalSpotify | None:
		id, type = self.extract_from_url(url)

		if id is None:
			return None
		if type is None:
			raise RessourceBadFormatException("❌ Spotify **%s** is not recognized.", url)

		tracks: (
			tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | TrackMinimalSpotify | None
		)
		try:
			if type == SpotifyType.PLAYLIST:
				tracks = await self.__spotify_search_id.get_playlist_tracks_by_id(id)
			elif type == SpotifyType.ARTIST:
				tracks = await self.__spotify_search_id.get_top_artist_by_id(id)
			elif type == SpotifyType.ALBUM:
				tracks = await self.__spotify_search_id.get_album_tracks_by_id(id)
			elif type == SpotifyType.TRACK:
				tracks = await self.__spotify_search_id.get_track_by_id(id)
			else:
				raise RessourceBadFormatException("❌ Spotify **%s** is not fully implemented. Try later.", type.name.lower())

		except SpotifyException as err:
			if err.http_status == 400:
				raise RessourceBadFormatException("❌ Spotify **%s** is a wrong URL format.", url)
			elif err.http_status == 404:
				raise RessourceNotExistsException("❌ Spotify **%s** is not accessible.", url)
			else:
				raise err
		return tracks

	@classmethod
	def extract_from_url(cls, url) -> tuple[str, SpotifyType | None] | tuple[None, None]:
		pattern = r"^(?:https?:\/\/)?(?:www\.)?open\.spotify\.com\/(?:\w{2}\/)?(?P<type>\w+)\/(?P<id>\w+)"
		match = re.search(pattern, url)
		if not match:
			return None, None
		type_str = match.group("type").upper()
		if type_str == "PLAYLIST":
			type = SpotifyType.PLAYLIST
		elif type_str == "ARTIST":
			type = SpotifyType.ARTIST
		elif type_str == "ALBUM":
			type = SpotifyType.ALBUM
		elif type_str == "TRACK":
			type = SpotifyType.TRACK
		else:
			type = None

		id = match.group("id")
		return id, type
