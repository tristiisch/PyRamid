import logging

from pyramid.connector.discord.services.api.annotation import pyramid_service


@pyramid_service()
class LoggerService:

	def __init__(self):
		self.__logger = logging.getLogger()

	def critical(self, msg, *args, **kwargs):
		self.__logger.critical(msg, *args, **kwargs)

	def error(self, msg, *args, **kwargs):
		self.__logger.error(msg, *args, **kwargs)

	def warning(self, msg, *args, **kwargs):
		self.__logger.warning(msg, *args, **kwargs)

	def info(self, msg, *args, **kwargs):
		self.__logger.info(msg, *args, **kwargs)

	def debug(self, msg, *args, **kwargs):
		self.__logger.debug(msg, *args, **kwargs)

	def log(self, level, msg, *args, **kwargs):
		self.__logger.log(msg, level, *args, **kwargs)
