import logging
import coloredlogs

from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.data.environment import Environment
from pyramid.api.services import IConfigurationService, ILoggerService

@pyramid_service()
class LoggerLevelService(ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			configuration_service: IConfigurationService
		):
		self.__logger_service = logger_service
		self.__configuration_service = configuration_service

	def start(self):
		logger = self.__logger_service.getLogger()
		# logger_colored = self.__logger_service.getLogger()
		logger_discord = logging.getLogger("discord")
		# logger_aiohttpweb = logging.getLogger("aiohttpweb")
		# logger_urllib3 = logging.getLogger("urllib3")
		logger_asyncio = logging.getLogger("asyncio")

		logger_dict = logging.root.manager.loggerDict
		active_loggers = [name for name in logger_dict if isinstance(logger_dict[name], logging.Logger)]
		if self.__configuration_service.mode == Environment.PRODUCTION:
			logger.setLevel("INFO")
			coloredlogs.set_level("INFO")
		else:
			logger.setLevel("DEBUG")
			coloredlogs.set_level("DEBUG")
			logger_discord.setLevel("INFO")
			logger_asyncio.setLevel("INFO")
