from discord import Guild, Interaction
from pyramid.api.services import IConfigurationService, IDiscordService, ILoggerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.discord.commands.tools.register import CommandRegister
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.source_type import SourceType


@pyramid_service()
class DiscordCommands(ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			configuration_service: IConfigurationService,
			discord_service: IDiscordService
		):
		self.__logger = logger_service
		self.__configuration_service = configuration_service
		self.__discord_service = discord_service

	def start(self):
		bot = self.__discord_service.bot
		command_prefix = self.__configuration_service.mode.name.lower()

		CommandRegister.import_commands()
		CommandRegister.create_commands(bot, command_prefix)
		CommandRegister.inject_commands()

		# @bot.tree.command(name="spam", description="Test spam")
		# async def cmd_spam(ctx: Interaction):
		# 	ms = MessageSenderQueued(ctx)
		# 	await ms.thinking()

		# 	for i in range(100):
		# 		ms.add_message(f"Spam n°{i}")
		# 	await ctx.response.send_message("Spam ended")

