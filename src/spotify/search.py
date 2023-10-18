import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from tools.abc import ASearch
from tools.object import TrackMinimalSpotify

class SpotifySearch(ASearch):
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret
		self.client_credentials_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
		self.client = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

	def search_tracks(self, search, limit=10) -> list[TrackMinimalSpotify] | None:
		results = self.client.search(q=search, limit=limit, type="track")

		if not results or not results.get('tracks') or not results['tracks'].get('items'):
			return None

		return [TrackMinimalSpotify(element) for element in results['tracks']['items']]

	def search_track(self, search) -> TrackMinimalSpotify | None:
		results = self.client.search(q=search, limit=1, type="track")
		
		if not results or not results.get('tracks') or not results['tracks'].get('items'):
			return None

		return TrackMinimalSpotify(results['tracks']['items'][0])
