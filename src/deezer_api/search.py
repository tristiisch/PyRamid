from enum import Enum
import deezer
import re
import requests

from tools.abc import ASearch
from tools.object import TrackMinimalDeezer


class DeezerSearch(ASearch):
	def __init__(self):
		self.client = deezer.Client()
		self.tools = DeezerTools()
		self.strict = False
		self.default_limit = 10

	def search_track(self, search) -> TrackMinimalDeezer | None:
		search_results = self.client.search(query=search)
		if not search_results or len(search_results) == 0:
			return None
		track = search_results[0]
		return TrackMinimalDeezer(track)

	def get_track_by_id(self, track_id: int) -> TrackMinimalDeezer | None:
		track = self.client.get_track(track_id)  # Todo handle HTTP errors
		if not track:
			return None
		return TrackMinimalDeezer(track)

	def search_tracks(self, search, limit=10) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search(query=search, strict=self.strict)

		if not search_results or len(search_results) == 0:
			return None
		tracks = search_results[:limit]
		return [TrackMinimalDeezer(element) for element in tracks]

	def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search_playlists(query=playlist_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		playlist = search_results[0]
		return [TrackMinimalDeezer(element) for element in playlist.get_tracks()]

	def get_playlist_tracks_by_id(self, playlist_id: int) -> list[TrackMinimalDeezer] | None:
		playlist = self.client.get_playlist(playlist_id)  # Todo handle HTTP errors
		if not playlist:
			return None
		last = [TrackMinimalDeezer(element) for element in playlist.get_tracks()]
		return last

	def get_album_tracks(self, album_name) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search_albums(query=album_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		album = search_results[0]
		return [TrackMinimalDeezer(element) for element in album.get_tracks()]

	def get_album_tracks_by_id(self, album_id: int) -> list[TrackMinimalDeezer] | None:
		album = self.client.get_album(album_id)  # Todo handle HTTP errors
		if not album:
			return None
		return [TrackMinimalDeezer(element) for element in album.get_tracks()]

	def get_top_artist(self, artist_name, limit=10) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search_artists(query=artist_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		artist = search_results[0]
		top_tracks = artist.get_top()[:limit]
		return [TrackMinimalDeezer(element) for element in top_tracks]

	def get_top_artist_by_id(self, artist_id: int, limit=10) -> list[TrackMinimalDeezer] | None:
		artist = self.client.get_artist(artist_id)  # Todo handle HTTP errors
		if not artist:
			return None
		top_tracks = artist.get_top()[:limit]
		return [TrackMinimalDeezer(element) for element in top_tracks]

	def get_by_url(self, url) -> list[TrackMinimalDeezer] | TrackMinimalDeezer | None:
		id, type = self.tools.extract_deezer_info(url)

		if id is None:
			return None
		if type is None:
			raise NotImplementedError(f"The type of deezer info '{url}' is not implemented")

		tracks: list[TrackMinimalDeezer] | TrackMinimalDeezer | None

		if type == DeezerType.PLAYLIST:
			tracks = self.get_playlist_tracks_by_id(id)
		elif type == DeezerType.ARTIST:
			tracks = self.get_top_artist_by_id(id)
		elif type == DeezerType.ALBUM:
			tracks = self.get_album_tracks_by_id(id)
		elif type == DeezerType.TRACK:
			tracks = self.get_track_by_id(id)
		else:
			raise NotImplementedError(f"The type of deezer info '{type}' can't be resolve")

		return tracks

	def search_exact_track(
		self, artist_name, album_title, track_title
	) -> TrackMinimalDeezer | None:
		search_results = self.client.search(
			artist=artist_name, album=album_title, track=track_title, strict=True
		)
		if not search_results:
			return None

		track = search_results[0]
		return TrackMinimalDeezer(track)


class DeezerType(Enum):
	PLAYLIST = 1
	ARTIST = 2
	ALBUM = 3
	TRACK = 4


class DeezerTools:
	def extract_deezer_info(self, url) -> tuple[int, DeezerType | None] | tuple[None, None]:
		# Resolve if URL is a deezer.page.link URL
		if "deezer.page.link" in url:
			response = requests.get(url, allow_redirects=True)
			url = response.url

		# Extract ID and type using regex
		pattern = r"(?<=deezer.com/fr/)(\w+)/(?P<id>\d+)"
		match = re.search(pattern, url)
		if match:
			deezer_type_str = match.group(1).upper()
			if deezer_type_str == "PLAYLIST":
				deezer_type = DeezerType.PLAYLIST
			elif deezer_type_str == "ARTIST":
				deezer_type = DeezerType.ARTIST
			elif deezer_type_str == "ALBUM":
				deezer_type = DeezerType.ALBUM
			elif deezer_type_str == "TRACK":
				deezer_type = DeezerType.TRACK
			else:
				deezer_type = None

			deezer_id = int(match.group("id"))
			return deezer_id, deezer_type
		else:
			return None, None
