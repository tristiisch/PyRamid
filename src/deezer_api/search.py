import deezer

from tools.abc import ASearch
from tools.object import TrackMinimalDeezer

class DeezerSearch(ASearch):
	def __init__(self):
		self.client = deezer.Client()

	def search_track(self, search) -> TrackMinimalDeezer | None:
		search_results = self.client.search(query=search)
		if not search_results or len(search_results) == 0:
			return None
		return TrackMinimalDeezer(search_results[0])

	def search_tracks(self, search, limit = 10) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search(query=search)

		if not search_results or len(search_results) == 0:
			return None
		return [TrackMinimalDeezer(element) for element in search_results[:limit]]

	def search_exact_track(self, artist_name, album_title, track_title) -> deezer.Track | None:
		search_results = self.client.search(
			artist=artist_name,
			album=album_title,
			track=track_title,
		)
		if search_results:
			track = search_results[0]
			return track
		else:
			return None
