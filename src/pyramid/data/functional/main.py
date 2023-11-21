import asyncio
import logging
import signal
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
		self.database_connection.connect()

	def clean_data(self):
		# Songs folder clear
		tools.clear_directory(self._config.deezer__folder)

	def start(self):
		# Discord Bot Instance
		discord_bot = DiscordBot(self.logger.getChild("Discord"), self._info, self._config)
		# Create bot
		discord_bot.create()

		loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

		def running(loop: asyncio.AbstractEventLoop):
			asyncio.set_event_loop(loop)

			# Run the asynchronous function in the thread without blocking it
			loop.create_task(discord_bot.start())
			try:
				# Run tasks in thread infinitly
				loop.run_forever()
			finally:
				loop.close()

		async def shutdown(loop: asyncio.AbstractEventLoop):
			await discord_bot.stop()
			loop.stop()

		def handle_signal(signum: int, frame):
			logging.info(f"Received signal {signum}. shutting down ...")
			asyncio.run_coroutine_threadsafe(shutdown(loop), loop)

		previous_handler = signal.signal(signal.SIGTERM, handle_signal)

		# Connect bot to Discord servers in his own thread
		thread = Thread(name="Discord", target=running, args=(loop,))
		thread.start()
		thread.join()

		signal.signal(signal.SIGTERM, previous_handler)

	def stop(self):
		logging.info("Wait for background tasks to stop")
		Queue.wait_for_end(5)
		logging.info("Bye bye")
