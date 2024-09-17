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
from pyramid.api.tasks.tools.register import TaskRegister
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

		logger.debug(ServiceRegister.get_dependency_tree())

		MainQueue.init()

		TaskRegister.import_tasks()
		TaskRegister.inject_tasks()
		TaskRegister.start_tasks()

  
	def stop(self):
		logging.info("Wait for background tasks to stop")
		Queue.wait_for_end(5)
		logging.info("Bye bye")
