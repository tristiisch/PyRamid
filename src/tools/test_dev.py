from logging import Logger
from tools.config import Config
from tools.git import GitInfo
from spotify.search import SpotifySearch
from deezer_api.search import DeezerSearch


class TestDev:
	def __init__(self, config: Config, logger: Logger):
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
