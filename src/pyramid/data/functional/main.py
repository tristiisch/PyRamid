import logging
from datetime import datetime
from threading import Thread

import tools.utils as tools
from connector.database.connection import DatabaseConnection
from connector.discord.bot import DiscordBot
from data.functional.application_info import ApplicationInfo
from tools.configuration.configuration import Configuration
from tools.logs_handler import LogsHandler
from tools.queue import Queue


class Main:
	def __init__(self):
		# Program information
		self._info = ApplicationInfo()

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
		self._config = Configuration(self.logger)
		self._config.load()

		self._logs_handler.set_log_level(self._config.mode)

	def database(self):
		# Database connection
		self.database_connection = DatabaseConnection(self._config)

	def clean_data(self):
		# Songs folder clear
		tools.clear_directory(self._config.deezer__folder)

	def start(self):
		# Discord Bot Instance
		discord_bot = DiscordBot(self.logger.getChild("Discord"), self._info, self._config)
		# Create bot
		discord_bot.create()

		# Connect bot to Discord servers
		thread = Thread(name="Discord", target=discord_bot.start)
		thread.start()
		thread.join()

	def stop(self):
		logging.info("Wait for background tasks to stop")
		Queue.wait_for_end(5)
		logging.info("Bye bye")
