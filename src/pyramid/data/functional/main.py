import argparse
import logging
import sys
from datetime import datetime
from threading import Thread

import tools.utils as tools
from data.functional.application_info import ApplicationInfo
from connector.deezer.downloader import DeezerDownloader
from connector.discord.bot import DiscordBot
from tools.configuration import Configuration
from tools.logs_handler import LogsHandler
from tools.queue import Queue


class Main:
	def __init__(self):
		# Program information
		self._info = ApplicationInfo()

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

		self._logs_handler = LogsHandler(self._info, log_dir, log_name, "error.log")
		self.logger = logging.getLogger()

		# Deletion of log files over 10
		tools.keep_latest_files(log_dir, 10, "error")

	# Logs management
	def git_info(self):
		self._info.load_git_info()
		logging.info(self._info)

	def config(self):
		# Config load
		self._config = Configuration()
		self._config.load()

		self._logs_handler.set_log_level(self._config.mode)

	def clean_data(self):
		# Songs folder clear
		tools.clear_directory(self._config.deezer_folder)

	def start(self):
		# Create Deezer player instance
		deezer_dl = DeezerDownloader(self._config.deezer_arl, self._config.deezer_folder)

		# Discord Bot Instance
		discord_bot = DiscordBot(
			self.logger.getChild("Discord"), self._info, self._config, deezer_dl
		)
		# Create bot
		discord_bot.create()

		# Connect bot to Discord servers
		thread = Thread(
			name="Discord",
			target=discord_bot.start
		)
		thread.start()
		thread.join()

	def stop(self):
		logging.info("Wait for background tasks to stop")
		Queue.wait_for_end(5)
		logging.info("Bye bye")
