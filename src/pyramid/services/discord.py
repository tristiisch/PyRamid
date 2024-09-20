import sys
import traceback
from typing import Dict

import discord
from discord import (
	Guild,
	Interaction,
	PrivilegedIntentsRequired,
)
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import (
	CommandNotFound,
	MissingPermissions,
	MissingRequiredArgument,
	CommandError,
)
from discord.app_commands.errors import AppCommandError, CommandInvokeError
from pyramid.api.services.configuration import IConfigurationService
from pyramid.data.environment import Environment
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.data.functional.engine_source import EngineSource
from pyramid.data.exceptions import DiscordMessageException
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.guild_instance import GuildInstances

from pyramid.api.services import IConfigurationService, IDiscordService, IInformationService, ILoggerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector


@pyramid_service(interface=IDiscordService)
class DiscordBotService(IDiscordService, ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService,
			information_service: IInformationService,
			configuration_service: IConfigurationService
		):
		self.__logger = logger_service
		self.__information_service = information_service
		self.__configuration_service = configuration_service

	def start(self):
		self.__engine_source = EngineSource(self.__configuration_service)

		intents = discord.Intents.default()
		# intents.members = True
		intents.message_content = True

		self.bot = Bot(
			command_prefix="$$",
			intents=intents,
			activity=discord.Activity(
				type=discord.ActivityType.listening,
				name=self.__information_service.get().get_version(),
			),
		)

		self.guilds_instances: Dict[int, GuildInstances] = {}
		self.__logger.info("Discord bot creating with discord.py v%s ...", discord.__version__)
		# self._health = health

		@self.bot.event
		async def on_command_error(ctx: Context, error: CommandError):
			if isinstance(error, CommandNotFound):
				await ctx.send("That command didn't exists !")
				return
			elif isinstance(error, MissingRequiredArgument):
				await ctx.send("Please pass in all requirements.")
				return
			elif isinstance(error, MissingPermissions):
				await ctx.send(
					"You dont have all the requirements or permissions for using this command :angry:"
				)
				return
			self.__logger.error("Command error from on_command_error : %s", error)

		@self.bot.event
		async def on_error(event, *args, **kwargs):
			# message = args[0] # Message object
			# traceback.extract_stack
			self.__logger.error("Error from on_error : %s", traceback.format_exc())
			# await bot.send_message(message.channel, "You caused an error!")

		async def on_tree_error(ctx: Interaction, app_error: AppCommandError, /):
			ms = MessageSenderQueued(ctx)

			if isinstance(app_error, CommandInvokeError):
				msg = ", ".join(app_error.args)
				error = app_error.original
			else:
				msg = "Error from on_tree_error"
				error = app_error
			trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
			self.__logger.error("%s :\n%s", msg, trace)

			discord_explanation = ":warning: You caused an error!"
			if isinstance(error, DiscordMessageException):
				ms.add_message(discord_explanation)
			else:
				attributes_dict = vars(ctx.namespace)
				formatted_attributes = " ".join(
					f"{key}: {value}"
					for key, value in attributes_dict.items()  # TODO Handle ENUM name instead of value
				)
				discord_explanation = (
					":warning: An error occurred while processing the command `/%s%s`"
					% (
						ctx.command.name if ctx.command else "<unknown command>",
						f" {formatted_attributes}" if formatted_attributes != "" else "",
					)
				)
				if self.__configuration_service.mode is not Environment.PRODUCTION:
					ms.add_code_message(trace, discord_explanation)
				else:
					ms.add_message(discord_explanation)

		self.bot.tree.on_error = on_tree_error

		@self.bot.event
		async def on_command(ctx: Context):
			self.__logger.debug("on_command :  %s", ctx.author)

	async def connect_bot(self):
		try:
			self.__logger.info("Discord bot login")
			await self.bot.login(self.__configuration_service.discord__token)
			self.__logger.info("Discord bot connecting")
			# self._health.discord = True
			await self.bot.connect()
		except PrivilegedIntentsRequired as ex:
			# self._health.discord = False
			self.__logger.critical(ex)
			sys.exit(1)

	async def disconnect_bot(self):
		# self.bot.clear()
		self.__logger.info("Discord bot stop")
		await self.bot.close()
		self.__logger.info("Discord bot stopped")

	def get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if guild.id not in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(
				guild, self.__logger.getChild(guild.name), self.__engine_source, self.__configuration_service.discord__ffmpeg
			)

		return self.guilds_instances[guild.id].cmds
