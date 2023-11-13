import logging
import time
import traceback
from logging import Logger
from typing import Dict

import discord
from discord import (
	Guild,
	PrivilegedIntentsRequired,
)
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import CommandNotFound, MissingPermissions, MissingRequiredArgument

from data.functional.application_info import ApplicationInfo
from data.environment import Environment
from data.guild_data import GuildData
from connector.discord.bot_cmd import BotCmd
from connector.discord.bot_listener import BotListener
from connector.discord.guild_cmd import GuildCmd
from connector.discord.guild_queue import GuildQueue
from data.functional.engine_source import EngineSource
from tools.configuration import Configuration


class DiscordBot:
	def __init__(
		self,
		logger: logging.Logger,
		information: ApplicationInfo,
		config: Configuration
	):
		self.__logger = logger
		self.__information = information
		self.__token = config.discord_token
		self.__ffmpeg = config.discord_ffmpeg
		self.__environment: Environment = config.mode
		self.__engine_source = EngineSource(config)
		self.__started = time.time()

		intents = discord.Intents.default()
		# intents.members = True
		intents.message_content = True

		bot = Bot(command_prefix="$$", intents=intents)
		self.bot = bot

		self.guilds_instances: Dict[int, GuildInstances] = {}

	def create(self):
		self.__logger.info("Discord bot creating with discord.py v%s ...", discord.__version__)
		self.listeners = BotListener(self.bot, self.__logger, self.__information)
		self.cmd = BotCmd(
			self.bot,
			self.__get_guild_cmd,
			self.__logger,
			self.__information,
			self.__environment,
			self.__started,
		)

		@self.bot.event
		async def on_command_error(ctx: Context, error):
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
			logging.error("Command error from on_command_error :  %s", error)

		@self.bot.event
		async def on_error(event, *args, **kwargs):
			# message = args[0] # Message object
			# traceback.extract_stack
			logging.error("Error from on_error : %s", traceback.format_exc())
			# await bot.send_message(message.channel, "You caused an error!")

		@self.bot.event
		async def on_command(ctx: Context):
			logging.debug("on_command :  %s", ctx.author)

		self.listeners.register()
		self.cmd.register()

	def start(self):
		self.__logger.info("Discord bot starting")
		try:
			self.bot.run(self.__token, log_handler=None)
		except PrivilegedIntentsRequired as ex:
			raise ex

	def __get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if guild.id not in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(
				guild,
				self.__logger.getChild(guild.name),
				self.__engine_source,
				self.__ffmpeg
			)

		return self.guilds_instances[guild.id].cmds


class GuildInstances:
	def __init__(
		self,
		guild: Guild,
		logger: Logger,
		engine_source: EngineSource,
		ffmpeg_path: str
	):
		self.data = GuildData(guild, engine_source)
		self.songs = GuildQueue(self.data, ffmpeg_path)
		self.cmds = GuildCmd(logger, self.data, self.songs, engine_source)
