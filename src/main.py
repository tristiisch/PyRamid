import logging
import tools.utils
import argparse

from datetime import datetime
from tools.config import Config
from discord.bot import DiscordBot
from deezer_api.downloader import DeezerDownloader
from spotify.search import SpotifySearch
from deezer_api.search import DeezerSearch
from tools.information import ProgramInformation
from tools.logs import Logger

class Main:
	def __init__(self):
		# Program information
		self._info = ProgramInformation()
    
	# Argument management
	def args(self):
		parser = argparse.ArgumentParser(description="Music Bot Discord using Deezer.")
		parser.add_argument("--version", action="store_true", help="Print version", required=False)
		args = parser.parse_args()

		if args.version:
			print(f"{self._info.name} v{self._info.version}")
			exit(1)

	# Logs management
	def logs(self):
		current_datetime = datetime.now()
		log_dir = "./logs"
		log_name = f"./{current_datetime.strftime('%Y_%m_%d %H_%M')}.log"

		# Deletion of log files over 10 
		tools.utils.keep_latest_files(log_dir, 10, "error")

		self._logs_handler = Logger(self._info, log_dir, log_name, "error.log")
		self.logger = logging.getLogger()

		logging.info(self._info)
	
	def config(self):
		# Config load
		self._config = Config()
		self._config.load()

		if self._config.mode == tools.utils.Mode.PRODUCTION:
			self.logger.setLevel("INFO")
		else:
			self.logger.setLevel("DEBUG")

	def clean_data(self):
		# Songs folder clear
		tools.utils.clear_directory(self._config.deezer_folder)

	def init(self):
		# Create Deezer player instance
		deezer_dl = DeezerDownloader(self._config.deezer_arl, self._config.deezer_folder)

		# Discord Bot Instance
		discord_bot = DiscordBot(logging.getLogger("Discord Global"), self._info, self._config, deezer_dl)
		# Create bot
		discord_bot.create()
		# Connect bot to Discord servers
		discord_bot.start()

	def test_spotify(self, input):
		spotify_search = SpotifySearch(self._config.spotify_client_id, self._config.spotify_client_secret)
		res = spotify_search.search_tracks(input, limit=10)
		if res == None:
			return
		for track in res:
			print(track)

	def test_deezer(self, input):
		deezer_search = DeezerSearch()
		res = deezer_search.search_tracks(input, limit=10)
		if res == None:
			return
		for track in res:
			print(track)

main = Main()

main.args()
main.logs()
main.config()
main.clean_data()
main.init()
