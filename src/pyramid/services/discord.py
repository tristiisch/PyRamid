import asyncio
import logging
import signal
from threading import Thread

from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.information import IInformationService
from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.discord.bot import DiscordBot
from pyramid.tools.custom_queue import Queue


# @pyramid_service()
class DiscordBotService(ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			information_service: IInformationService,
			configuration_service: IConfigurationService
		):
		self.__logger_service = logger_service
		self.__information_service = information_service
		self.__configuration_service = configuration_service

	def start(self):
		self.discord_bot = DiscordBot(self.__logger_service.getChild("Discord"), self.__information_service.get(), self.__configuration_service)
		self.discord_bot.create()

		loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

		def running(loop: asyncio.AbstractEventLoop):
			asyncio.set_event_loop(loop)

			loop.create_task(self.discord_bot.start())
			try:
				loop.run_forever()
			finally:
				loop.close()

		async def shutdown(loop: asyncio.AbstractEventLoop):
			await self.discord_bot.stop()
			loop.stop()

		def handle_signal(signum: int, frame):
			logging.info("Received signal %d. shutting down ..." % signum)
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
