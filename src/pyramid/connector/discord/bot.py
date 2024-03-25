import logging
import sys
import time
import traceback
from logging import Logger
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
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.data.environment import Environment
from pyramid.data.guild_data import GuildData
from pyramid.connector.discord.bot_cmd import BotCmd
from pyramid.connector.discord.bot_listener import BotListener
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.connector.discord.guild_queue import GuildQueue
from pyramid.data.functional.engine_source import EngineSource
from pyramid.data.exceptions import DiscordMessageException
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.health import HealthModules
from pyramid.connector.discord.music_player_interface import MusicPlayerInterface
from pyramid.tools.configuration.configuration import Configuration


class DiscordBot:
	def __init__(self, logger: logging.Logger, information: ApplicationInfo, config: Configuration):
		self.__logger = logger
		self.__information = information
		self.__token = config.discord__token
		self.__ffmpeg = config.discord__ffmpeg
		self.__environment: Environment = config.mode
		self.__engine_source = EngineSource(config)
		self.__started = time.time()

		intents = discord.Intents.default()
		# intents.members = True
		intents.message_content = True

		bot = Bot(
			command_prefix="$$",
			intents=intents,
			activity=discord.Activity(
				type=discord.ActivityType.listening,
				name=f"{self.__information.get_version()}",
			),
		)
		self.bot = bot

		self.guilds_instances: Dict[int, GuildInstances] = {}

	def create(self, health: HealthModules):
		self.__logger.info("Discord bot creating with discord.py v%s ...", discord.__version__)
		self.listeners = BotListener(self.bot, self.__logger)
		self.cmd = BotCmd(
			self.bot,
			self.__get_guild_cmd,
			self.__logger,
			self.__information,
			self.__environment,
			self.__started,
		)
		self._health = health

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
			logging.error("Command error from on_command_error : %s", error)

		@self.bot.event
		async def on_error(event, *args, **kwargs):
			# message = args[0] # Message object
			# traceback.extract_stack
			logging.error("Error from on_error : %s", traceback.format_exc())
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
			logging.error("%s :\n%s", msg, trace)

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
				if self.__environment is not Environment.PRODUCTION:
					ms.add_code_message(trace, discord_explanation)
				else:
					ms.add_message(discord_explanation)

		self.bot.tree.on_error = on_tree_error

		@self.bot.event
		async def on_command(ctx: Context):
			logging.debug("on_command :  %s", ctx.author)

		self.listeners.register()
		self.cmd.register()

	async def start(self):
		try:
			# self.bot.run(self.__token, log_handler=None)
			self.__logger.info("Discord bot login")
			await self.bot.login(self.__token)
			self.__logger.info("Discord bot connecting")
			self._health.discord = True
			await self.bot.connect()
		except PrivilegedIntentsRequired as ex:
			self._health.discord = False
			self.__logger.critical(ex)
			sys.exit(1)

	async def stop(self):
		# self.bot.clear()
		logging.info("Discord bot stop")
		await self.bot.close()
		logging.info("Discord bot stopped")

	def __get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if guild.id not in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(
				guild, self.__logger.getChild(guild.name), self.__engine_source, self.__ffmpeg
			)

		return self.guilds_instances[guild.id].cmds


class GuildInstances:
	def __init__(self, guild: Guild, logger: Logger, engine_source: EngineSource, ffmpeg_path: str):
		self.data = GuildData(guild, engine_source)
		self.mpi = MusicPlayerInterface(self.data.guild.preferred_locale, self.data.track_list)
		self.songs = GuildQueue(self.data, ffmpeg_path, self.mpi)
		self.cmds = GuildCmd(logger, self.data, self.songs, engine_source)
		self.mpi.set_queue_action(self.cmds)
