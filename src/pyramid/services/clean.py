import logging
import coloredlogs

from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.api.services.configuration import IConfigurationService
from pyramid.tools import utils

@pyramid_service()
class LoggerLevelService(ServiceInjector):

	def injectService(self,
			configuration_service: IConfigurationService
		):
		self.__configuration_service = configuration_service

	def start(self):
		# Songs folder clear
		utils.clear_directory(self.__configuration_service.deezer__folder)
