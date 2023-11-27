import re
from enum import Enum
from typing import Any

import spotipy
from data.a_engine_tools import AEngineTools
from data.a_search import ASearch, ASearchId
from data.track import TrackMinimalSpotify
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifySearchBase(ASearch):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		self.default_limit = default_limit
		self.client_id = client_id
		self.client_secret = client_secret
		self.client_credentials_manager = SpotifyClientCredentials(
			client_id=self.client_id, client_secret=self.client_secret
		)
		self.client = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
		self.tools = SpotifyTools()

	def _get_all_tracks(self, results: Any, item_name = "items") -> None | list[dict[str, Any]]:
		if not results:
			return None
		tracks: list = results[item_name]

		while results["next"]:
			results = self.client.next(results)
			tracks.extend(results[item_name])

		return tracks


class SpotifySearchId(ASearchId, SpotifySearchBase):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		super().__init__(default_limit, client_id, client_secret)

	def get_track_by_id(self, track_id: str) -> TrackMinimalSpotify | None:
		results = self.client.track(track_id=track_id)

		return TrackMinimalSpotify(results)

	def get_playlist_tracks_by_id(
		self, playlist_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks = self._get_all_tracks(self.client.playlist_tracks(playlist_id=playlist_id))
		if not tracks:
			return None
		return [TrackMinimalSpotify(element["track"]) for element in tracks], []

	def get_album_tracks_by_id(
		self, album_id: str
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		tracks = self._get_all_tracks(self.client.album_tracks(album_id=album_id))
		if not tracks:
			return None
		return [TrackMinimalSpotify(element["track"]) for element in tracks], []

	def get_top_artist_by_id(
		self, artist_id: str, limit: int | None = None
	) -> tuple[list[TrackMinimalSpotify], list[TrackMinimalSpotify]] | None:
		if limit is None:
			limit = self.default_limit
		results = self.client.artist_top_tracks(artist_id=artist_id)

		if not results or not results.get("tracks"):
			return None

		tracks = results["tracks"]
		if len(tracks) > limit:
			tracks = tracks[:limit]
		return [TrackMinimalSpotify(element) for element in tracks], []


class SpotifySearch(SpotifySearchId):
	def __init__(self, default_limit: int, client_id: str, client_secret: str):
		super().__init__(default_limit, client_id, client_secret)

	def search_tracks(self, search, limit: int | None = None) -> list[TrackMinimalSpotify] | None:
		if limit is None:
			limit = self.default_limit
		results = self.client.search(q=search, limit=limit, type="track")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		return [TrackMinimalSpotify(element) for element in tracks]

	def search_track(self, search) -> TrackMinimalSpotify | None:
		results = self.client.search(q=search, limit=1, type="track")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		track = tracks[0]

		return TrackMinimalSpotify(track)

	def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalSpotify] | None:
		results = self.client.search(q=playlist_name, limit=1, type="playlist")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		return [TrackMinimalSpotify(element) for element in tracks]

	def get_album_tracks(self, album_name) -> list[TrackMinimalSpotify] | None:
		results = self.client.search(q=album_name, limit=1, type="album")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		return [TrackMinimalSpotify(element) for element in tracks]

	def get_top_artist(self, artist_name, limit: int | None = None) -> list[TrackMinimalSpotify] | None:
		results = self.client.search(q=artist_name, limit=1, type="artist")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		return [TrackMinimalSpotify(element) for element in tracks]

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
			tracks = self.get_playlist_tracks_by_id(id)
		elif type == SpotifyType.ARTIST:
			tracks = self.get_top_artist_by_id(id)
		elif type == SpotifyType.ALBUM:
			tracks = self.get_album_tracks_by_id(id)
		elif type == SpotifyType.TRACK:
			tracks = self.get_track_by_id(id)
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
		pattern = r"(?<=open.spotify.com/)(intl-(?P<intl>\w+)/)(?P<type>\w+)/(?P<id>\w+)"
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
