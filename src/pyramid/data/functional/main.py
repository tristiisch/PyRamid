import argparse
import asyncio
import logging
import sys
import signal
from datetime import datetime
from threading import Thread

from pyramid.connector.discord.services.api.register import get_service, register_services
from pyramid.connector.discord.services.environment import EnvironmentService
from pyramid.tools import utils
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.connector.discord.bot import DiscordBot
from pyramid.client.server import SocketServer
from pyramid.data.health import HealthModules
from pyramid.tools.configuration.configuration import Configuration
from pyramid.tools.logs_handler import LogsHandler
from pyramid.tools.custom_queue import Queue


class Main:
	def __init__(self):
		# Program information
		self._info = ApplicationInfo()
		self._health = HealthModules()
		self._discord_bot = None

	# Argument management
	def args(self):
		parser = argparse.ArgumentParser(description="Music Bot Discord using Deezer.")
		parser.add_argument("--version", action="store_true", help="Print version", required=False)
		args = parser.parse_args()

		if args.version:
			print(f"{self._info.get_version()}")
			sys.exit(0)

	# Logs management
	def logs(self):
		current_datetime = datetime.now()
		log_dir = "./logs"
		log_name = f"./{current_datetime.strftime('%Y_%m_%d %H_%M')}.log"

		self._logs_handler = LogsHandler()
		self._logs_handler.init(self._info, log_dir, log_name, "error.log")
		self.logger = logging.getLogger()

		# Deletion of log files over 10
		utils.keep_latest_files(log_dir, 10, "error")

	def config(self):
		# Config load
		self._config = Configuration(self.logger)
		self._config.load()
		self._health.configuration = True

		self._logs_handler.set_log_level(self._config.mode)

	def open_socket(self):
		self.socket_server = SocketServer(self.logger.getChild("socket"), self._health)
		thread = Thread(name="Socket", target=self.socket_server.start_server, daemon=True)
		thread.start()

	def clean_data(self):
		# Songs folder clear
		utils.clear_directory(self._config.deezer__folder)

	def start(self):
		# Discord Bot Instance
		discord_bot = DiscordBot(self.logger.getChild("Discord"), self._info, self._config)
		# Create bot
		discord_bot.create(self._health)

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

		# -- Service [TEMP]
		self._discord_bot = discord_bot
		if self._discord_bot is None:
			raise Exception("Bot is not connected")
		register_services(self._discord_bot.bot, self.logger)
		environment_service = get_service("EnvironmentService")
		self.logger.info("environment_service %s" % environment_service)
		if not isinstance(environment_service, EnvironmentService):
			raise Exception("environment_service is not from type EnvironmentService, got %s" % type(environment_service))
		environment_service.set_type(self._config.mode)
		# --

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
