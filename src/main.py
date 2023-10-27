import logging
import sys
import argparse
import tools.utils

from datetime import datetime
from spotify.search import SpotifySearch
from deezer_api.downloader import DeezerDownloader
from deezer_api.search import DeezerSearch
from discord.bot import DiscordBot
from tools.config import Config
from tools.information import ProgramInformation
from tools.logs import Logger
from tools.git import GitInfo


class Main:
	def __init__(self):
		# Program information
		self._info = ProgramInformation()

	# Argument management
	def args(self):
		parser = argparse.ArgumentParser(description="Music Bot Discord using Deezer.")
		parser.add_argument("--version", action="store_true", help="Print version", required=False)
		parser.add_argument(
			"--git", action="store_true", help="Print git informations", required=False
		)
		args = parser.parse_args()

		if args.version:
			self._info.load_git_info()
			print(f"{self._info.to_json()}")
			sys.exit(0)
		elif args.git:
			self._info.load_git_info()
			print(f"{self._info.git_info.to_json()}")
			sys.exit(0)

	# Logs management
	def logs(self):
		current_datetime = datetime.now()
		log_dir = "./logs"
		log_name = f"./{current_datetime.strftime('%Y_%m_%d %H_%M')}.log"

		self._logs_handler = Logger(self._info, log_dir, log_name, "error.log")
		self.logger = logging.getLogger()

		# Deletion of log files over 10
		tools.utils.keep_latest_files(log_dir, 10, "error")

	# Logs management
	def git_info(self):
		self._info.load_git_info()
		logging.info(self._info)

	def config(self):
		# Config load
		self._config = Config()
		self._config.load()

		self._logs_handler.set_log_level(self._config.mode)

	def clean_data(self):
		# Songs folder clear
		tools.utils.clear_directory(self._config.deezer_folder)

	def init(self):
		# Create Deezer player instance
		deezer_dl = DeezerDownloader(self._config.deezer_arl, self._config.deezer_folder)

		# Discord Bot Instance
		discord_bot = DiscordBot(
			self.logger.getChild("Discord"), self._info, self._config, deezer_dl
		)
		# Create bot
		discord_bot.create()
		# Connect bot to Discord servers
		discord_bot.start()

	def test_spotify(self, input):
		spotify_search = SpotifySearch(
			self._config.spotify_client_id, self._config.spotify_client_secret
		)
		res = spotify_search.search_tracks(input, limit=10)
		if res is None:
			return
		for track in res:
			print(track)

	def test_deezer(self, input):
		deezer_search = DeezerSearch()
		res = deezer_search.search_tracks(input, limit=10)
		if res is None:
			return
		for track in res:
			print(track)

	def test_git(self):
		t = GitInfo()
		t.get()
		t.save()

		t2 = GitInfo.read()
		if t2:
			print(vars(t2))


main = Main()

main.args()
main.logs()
main.git_info()
main.config()
main.clean_data()
main.init()
