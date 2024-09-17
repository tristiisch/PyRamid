from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.discord import IDiscordService
from pyramid.api.services.information import IInformationService
from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.discord.bot import DiscordBot


@pyramid_service(interface=IDiscordService)
class DiscordBotService(IDiscordService, ServiceInjector):

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
