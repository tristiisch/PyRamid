import logging
import logging.handlers
import os
import sys

import coloredlogs
import tools.utils as tools
from data.functional.application_info import ApplicationInfo
from data.environment import Environment


class LogsHandler:
	def __init__(self):
		self.__date = "%d/%m/%Y %H:%M:%S"
		self.__console_format = "%(asctime)s %(levelname)s %(message)s"
		self.__file_format = "[{asctime}] [{levelname:<8}] {name}: {message}"

	def init(self, info: ApplicationInfo, logs_dir, log_filename, error_filename):
		self.__info = info
		self.__logs_dir = logs_dir
		self.__log_filename = log_filename
		self.__error_filename = error_filename

		self.logger = logging.getLogger()

		self.log_to_console()
		self.log_to_file()
		self.log_to_file_exceptions()

	def log_to_console(self):
		coloredlogs.install(fmt=self.__console_format, datefmt=self.__date)

	def log_to_file(self):
		log_filename = os.path.join(self.__logs_dir, self.__log_filename)
		tools.create_parent_directories(log_filename)

		file_handler = logging.handlers.RotatingFileHandler(
			filename=log_filename,
			encoding="utf-8",
			maxBytes=512 * 1024 * 1024,  # 512 Mo
		)

		formatter = logging.Formatter(self.__file_format, self.__date, style="{")
		file_handler.setFormatter(formatter)

		logging.getLogger().addHandler(file_handler)

	def log_to_file_exceptions(self):
		log_filename = os.path.join(self.__logs_dir, self.__error_filename)

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
		# Create a critical level log message with info from the except hook.
		self.logger_unhandled_exception.critical(
			self.__info, exc_info=(exc_type, exc_value, exc_traceback)
		)

	def set_log_level(self, mode: Environment):
		if mode == Environment.PRODUCTION:
			self.logger.setLevel("INFO")
		else:
			self.logger.setLevel("DEBUG")
			# coloredlogs.set_level("DEBUG")
		coloredlogs.set_level("INFO")
