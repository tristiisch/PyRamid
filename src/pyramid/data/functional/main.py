import argparse
import asyncio
import logging
import sys
import signal
from threading import Thread

from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.information import IInformationService
from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.connector.discord.bot import DiscordBot
from pyramid.tools.custom_queue import Queue
from pyramid.tools.main_queue import MainQueue


class Main:
	def __init__(self):
		# Program information
		self._info = ApplicationInfo()
		# self._health = HealthModules()
		self._discord_bot = None

	# Argument management
	def args(self):
		parser = argparse.ArgumentParser(description="Music Bot Discord using Deezer.")
		parser.add_argument("--version", action="store_true", help="Print version", required=False)
		args = parser.parse_args()

		if args.version:
			print(f"{self._info.get_version()}")
			sys.exit(0)

	def start(self):
		ServiceRegister.import_services()
		ServiceRegister.create_services()
		ServiceRegister.inject_services()
		ServiceRegister.start_services()

		logger = ServiceRegister.get_service(ILoggerService)
		info = ServiceRegister.get_service(IInformationService)
		config = ServiceRegister.get_service(IConfigurationService)

		logger.debug(ServiceRegister.get_dependency_tree())

		MainQueue.init()

		# Discord Bot Instance
		discord_bot = DiscordBot(logger.getChild("Discord"), info.get(), config)
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

		# def running_async(discord_bot: DiscordBot):
		# 	asyncio.run(discord_bot.start())

		# thread = Thread(name="Discord", target=running_async, args=(discord_bot,))
		# thread.start()
		# thread.join()

  
	def stop(self):
		logging.info("Wait for background tasks to stop")
		Queue.wait_for_end(5)
		logging.info("Bye bye")
