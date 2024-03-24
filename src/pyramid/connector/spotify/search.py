import re
from enum import Enum
from typing import Any

from data.a_engine_tools import AEngineTools
from data.a_search import ASearch, ASearchId
from data.track import TrackMinimalSpotify
from spotipy.oauth2 import SpotifyClientCredentials

from connector.spotify.cli_spotify import CliSpotify


class SpotifySearchBase(ASearch):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		self.default_limit = default_limit
		self.client_id = client_id
		self.client_secret = client_secret
		self.client_credentials_manager = SpotifyClientCredentials(
			client_id=self.client_id, client_secret=self.client_secret
		)
		self.client = CliSpotify(client_credentials_manager=self.client_credentials_manager)
		self.tools = SpotifyTools()

	async def items(self, results: dict[str, Any], item_name="items") -> None | list[dict[str, Any]]:
		if not results:
			return None
		tracks: list = results[item_name]

		while results["next"]:
			results = await self.client.async_next(results)# type: ignore
			tracks.extend(results[item_name])

		return tracks

	async def items_max(self, results: dict[str, Any], limit: int | None = None, item_name="items"):
		if not results or not results.get("tracks") or not results["tracks"].get(item_name):
			return None

		if limit is None:
			limit = self.default_limit
		tracks: list[Any] = results["tracks"][item_name]

		results_tracks: dict[str, Any] = results["tracks"]
		while results["tracks"]["next"] and limit > len(tracks):
			results = await self.client.async_next(results_tracks)  # type: ignore
			tracks.extend(results_tracks[item_name])

		if len(tracks) > limit:
			return tracks[:limit]

		return tracks


class SpotifySearchId(ASearchId, SpotifySearchBase):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		super().__init__(default_limit, client_id, client_secret)

	async def get_track_by_id(self, track_id: str) -> TrackMinimalSpotify | None:
		result = await self.client.async_track(track_id=track_id)
		if not result:
			return None
		return TrackMinimalSpotify(result)

	async def get_playlist_tracks_by_id(
		self, playlist_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks_playlist = await self.items(
			await self.client.async_playlist_items(playlist_id=playlist_id)
		)
		if not tracks_playlist:
			return None
		return [TrackMinimalSpotify(element["track"]) for element in tracks_playlist], []

	async def get_album_tracks_by_id(
		self, album_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks = await self.items(await self.client.async_album_tracks(album_id=album_id))
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
			limit = self.default_limit
		results = await self.client.async_artist_top_tracks(artist_id)

		if not results or not results.get("tracks"):
			return None

		tracks = results["tracks"]
		if len(tracks) > limit:
			tracks = tracks[:limit]
		return [TrackMinimalSpotify(element) for element in tracks], []


class SpotifyResponse:
	def __init__(self, client: CliSpotify, default_limit: int, item_name="items") -> None:
		self.client = client
		self.default_limit = default_limit
		self.item_name = item_name

	async def items(self, results: dict[str, Any], limit: int | None = None):
		if not results or not results.get("tracks") or not results["tracks"].get(self.item_name):
			return None

		if limit is None:
			limit = self.default_limit
		tracks: list[Any] = results["tracks"][self.item_name]

		results_tracks: dict[str, Any] = results["tracks"]
		while results["tracks"]["next"] and limit > len(tracks):
			results = await self.client.async_next(results_tracks)  # type: ignore
			tracks.extend(results_tracks[self.item_name])

		if len(tracks) > limit:
			return tracks[:limit]

		return tracks


class SpotifySearch(SpotifySearchId):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		super().__init__(default_limit, client_id, client_secret)

	async def search_tracks(
		self, search, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		if limit is None:
			limit = self.default_limit
		if limit > 50:
			req_limit = 50
		else:
			req_limit = limit
		results = await self.client.async_search(q=search, limit=req_limit, type="track")
		tracks = await self.items_max(results, limit)
		if not tracks:
			return None
		return [TrackMinimalSpotify(element) for element in tracks]

	async def search_track(self, search) -> TrackMinimalSpotify | None:
		results = await self.client.async_search(q=search, limit=1, type="track")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		track = tracks[0]

		return TrackMinimalSpotify(track)

	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalSpotify] | None:
		results = await self.client.async_search(q=playlist_name, limit=1, type="playlist")

		if not results or not results.get("playlists") or not results["playlists"].get("items"):
			return None

		playlist_id = results["playlists"]["items"][0]["id"]
		tracks = await self.get_playlist_tracks_by_id(playlist_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_album_tracks(self, album_name) -> list[TrackMinimalSpotify] | None:
		results = await self.client.async_search(q=album_name, limit=1, type="album")

		if not results or not results.get("albums") or not results["albums"].get("items"):
			return None

		album_id = results["albums"]["items"][0]["id"]
		tracks = await self.get_album_tracks_by_id(album_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_top_artist(
		self, artist_name, limit: int | None = None
	) -> list[TrackMinimalSpotify] | None:
		results = await self.client.async_search(q=artist_name, limit=1, type="artist")

		if not results or not results.get("artists") or not results["artists"].get("items"):
			return None

		artist_id = results["artists"]["items"][0]["id"]
		tracks = await self.get_top_artist_by_id(artist_id)
		if not tracks:
			return None
		return tracks[0]

	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | TrackMinimalSpotify | None:
		id, type = self.tools.extract_from_url(url)

		if id is None:
			return None
		if type is None:
			raise NotImplementedError(f"The type of spotify info '{url}' is not implemented")

		tracks: (
			tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | TrackMinimalSpotify | None
		)

		if type == SpotifyType.PLAYLIST:
			tracks = await self.get_playlist_tracks_by_id(id)
		elif type == SpotifyType.ARTIST:
			tracks = await self.get_top_artist_by_id(id)
		elif type == SpotifyType.ALBUM:
			tracks = await self.get_album_tracks_by_id(id)
		elif type == SpotifyType.TRACK:
			tracks = await self.get_track_by_id(id)
		else:
			raise NotImplementedError(f"The type of spotify info '{type}' can't be resolve")

		return tracks


class SpotifyType(Enum):
	PLAYLIST = 1
	ARTIST = 2
	ALBUM = 3
	TRACK = 4


class SpotifyTools(AEngineTools):
	def extract_from_url(self, url) -> tuple[str, SpotifyType | None] | tuple[None, None]:
		# Extract ID and type using regex
		pattern = r"(?<=open\.spotify\.com/)(intl-(?P<intl>\w+)/)?(?P<type>\w+)/(?P<id>\w+)"
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
