import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from tools.abc import ASearch
from tools.object import TrackMinimalSpotify


class SpotifySearch(ASearch):
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret
		self.client_credentials_manager = SpotifyClientCredentials(
			client_id=self.client_id, client_secret=self.client_secret
		)
		self.client = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

	def search_tracks(self, search, limit=10) -> list[TrackMinimalSpotify] | None:
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

	def get_top_artist(self, artist_name, limit=10) -> list[TrackMinimalSpotify] | None:
		results = self.client.search(q=artist_name, limit=1, type="artist")

		if not results or not results.get("tracks") or not results["tracks"].get("items"):
			return None

		tracks = results["tracks"]["items"]
		return [TrackMinimalSpotify(element) for element in tracks]

	def get_by_url(self, url) -> list[TrackMinimalSpotify] | TrackMinimalSpotify | None:
		raise NotImplementedError("Get by url for spotify is not implemted")
