from logging import Logger
import random

# from faker import Faker
from connector.deezer.search import DeezerSearch
from data.functional.git_info import GitInfo
from connector.database.obj.user import User, UserHandler
from tools.configuration.configuration import Configuration
from connector.spotify.search import SpotifySearch


class TestDev:
	def __init__(self, config: Configuration, logger: Logger):
		self._config = config
		self.logger = logger

	def test_spotify(self, input):
		spotify_search = SpotifySearch(
			self._config.general__limit_tracks,
			self._config.spotify__client_id,
			self._config.spotify__client_secret,
		)
		res = spotify_search.search_tracks(input, limit=10)
		if res is None:
			return
		for track in res:
			self.logger.info(track)

	def test_deezer(self, input):
		deezer_search = DeezerSearch(self._config.general__limit_tracks)
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

	def test_db(self):
		# fake = Faker()

		# if random.randint(0, 1) == 1:
		# 	name="%s %s" % (fake.first_name(), fake.last_name())
		# else:
		name="Jacob Collins"

		user_handler = UserHandler()

		user_handler.find(name)

		user = User(name=name, age=random.randint(18, 99))
		is_new = user_handler.add_or_update(user)

		user_handler.find_all()

		if is_new is True:
			user_handler.delete(name)
