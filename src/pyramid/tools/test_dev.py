from logging import Logger

from connector.deezer.search import DeezerSearch
from data.functional.git_info import GitInfo
from tools.configuration import Configuration
from connector.spotify.search import SpotifySearch


class TestDev:
	def __init__(self, config: Configuration, logger: Logger):
		self._config = config
		self.logger = logger

	def test_spotify(self, input):
		spotify_search = SpotifySearch(
			self._config.spotify_client_id, self._config.spotify_client_secret
		)
		res = spotify_search.search_tracks(input, limit=10)
		if res is None:
			return
		for track in res:
			self.logger.info(track)

	def test_deezer(self, input):
		deezer_search = DeezerSearch()
		res = deezer_search.search_tracks(input, limit=10)
		if res is None:
			return
		for track in res:
			self.logger.info(track)

	def test_git(self):
		t = GitInfo()
		t.get()
		t.save()

		t2 = GitInfo.read()
		if t2:
			self.logger.info(vars(t2))
