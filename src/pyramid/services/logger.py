import logging
import logging.handlers
import os
import sys
import coloredlogs
from datetime import datetime

from pyramid.api.services.information import IInformationService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.data.environment import Environment
from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.logger import ILoggerService
from pyramid.tools import utils

from pyramid.tools import utils

@pyramid_service(interface=ILoggerService)
class LoggerService(ILoggerService, ServiceInjector):

	def __init__(self):
		self.__date = "%d/%m/%Y %H:%M:%S"
		self.__console_format = "%(asctime)s %(levelname)s %(message)s"
		self.__file_format = "[{asctime}] [{levelname:<8}] {name}: {message}"
		self.logger = logging.getLogger()
		self.logger.setLevel("INFO")
		current_datetime = datetime.now()
		self.__logs_dir = "./logs"
		self.__log_filename = "./%s.log" % current_datetime.strftime('%Y_%m_%d %H_%M')
		self.__error_filename = "./error.log"

	def injectService(self,
			information_service: IInformationService
		):
		self.__information_service = information_service

	def start(self):
		self.__enable_log_to_console()
		self.__enable_log_to_file()
		self.__enable_log_to_file_exceptions()

		self.logger.info("────────────────────────────────────────────")
		self.logger.info(self.__information_service.get())

		# Deletion of log files over 10
		utils.keep_latest_files(self.__logs_dir, 10, "error")

	def critical(self, msg, *args, **kwargs):
		self.logger.critical(msg, *args, **kwargs)

	def error(self, msg, *args, **kwargs):
		self.logger.error(msg, *args, **kwargs)

	def warning(self, msg, *args, **kwargs):
		self.logger.warning(msg, *args, **kwargs)

	def info(self, msg, *args, **kwargs):
		self.logger.info(msg, *args, **kwargs)

	def debug(self, msg, *args, **kwargs):
		self.logger.debug(msg, *args, **kwargs)

	def log(self, level, msg, *args, **kwargs):
		self.logger.log(msg, level, *args, **kwargs)

	def getLogger(self) -> logging.Logger:
		return self.logger

	def getChild(self, suffix: str) -> logging.Logger:
		return self.logger.getChild(suffix)

	def __enable_log_to_console(self):
		coloredlogs.install(fmt=self.__console_format, datefmt=self.__date, isatty=True)
		coloredlogs.set_level("INFO")

	def __enable_log_to_file(self):
		log_filename = os.path.join(self.__logs_dir, self.__log_filename)
		utils.create_parent_directories(log_filename)

		file_handler = logging.handlers.RotatingFileHandler(
			filename=log_filename,
			encoding="utf-8",
			maxBytes=512 * 1024 * 1024,  # 512 Mo
		)

		formatter = logging.Formatter(self.__file_format, self.__date, style="{")
		file_handler.setFormatter(formatter)

		self.logger.addHandler(file_handler)

	def __enable_log_to_file_exceptions(self):
		log_filename = os.path.join(self.__logs_dir, self.__error_filename)
		utils.create_parent_directories(log_filename)

		file_handler = logging.handlers.RotatingFileHandler(
			filename=log_filename,
			encoding="utf-8",
			maxBytes=10 * 1024 * 1024,  # 10 Mo
			backupCount=10,
		)

		formatter = logging.Formatter(self.__file_format, self.__date, style="{")
		file_handler.setFormatter(formatter)

		# Retrieves warning exceptions and above
		file_handler.setLevel("WARNING")
		logging.getLogger().addHandler(file_handler)

		# Retrieves unhandled exceptions
		self.logger_unhandled_exception = logging.getLogger("Unhandled Exception")
		self.logger_unhandled_exception.addHandler(file_handler)
		sys.excepthook = self.__handle_unhandled_exception

	def __handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			# Will call default excepthook
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			return
		info = self.__information_service.get()
		# Create a critical level log message with info from the except hook.
		self.logger_unhandled_exception.critical(
			info, exc_info=(exc_type, exc_value, exc_traceback)
		)
