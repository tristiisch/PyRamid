import math
from logging import Logger
import time
from typing import Callable

from discord import Guild, Interaction
from discord.ext.commands import Bot
from pyramid.connector.discord.commands.about_command import AboutCommand
from pyramid.connector.discord.commands.api.parameters import ParametersCommand
from pyramid.connector.discord.commands.api.register import register_commands
from pyramid.connector.discord.commands.help_command import HelpCommand
from pyramid.connector.discord.commands.ping_command import PingCommand
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.data.environment import Environment
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.functional.engine_source import SourceType


class BotCmd:
	def __init__(
		self,
		bot: Bot,
		get_guild_cmd: Callable[[Guild], GuildCmd],
		logger: Logger,
		info: ApplicationInfo,
		environment: Environment
	):
		self.__bot = bot
		self.__get_guild_cmd = get_guild_cmd
		self.__logger = logger
		self.__info = info
		self.__environment = environment

	def register(self):
		bot = self.__bot

		services: dict[str, object] = dict()

		service = self.__environment
		service_name = service.__class__.__name__
		services[service_name] = service

		service = self.__info
		service_name = service.__class__.__name__
		services[service_name] = service
		
		register_commands(services, self.__bot, self.__logger, self.__environment.name.lower())

		# ping = PingCommand(ParametersCommand("ping"), self.__bot, self.__logger)
		# ping.register(self.__environment.name.lower())

		# about = AboutCommand(self.__bot, self.__logger, self.__started, self.__environment, self.__info)
		# about.register(self.__environment.name.lower())

		# help = HelpCommand(self.__bot, self.__logger)
		# help.register(self.__environment.name.lower())

		@bot.tree.command(name="play", description="Adds a track to the end of the queue and plays it")
		async def cmd_play(ctx: Interaction, input: str, engine: SourceType | None):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play(ms, ctx, input, engine)

		@bot.tree.command(name="play_next", description="Plays a track next the current one")
		async def cmd_play_next(ctx: Interaction, input: str, engine: SourceType | None):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play(ms, ctx, input, engine, at_end=False)

		@bot.tree.command(name="pause", description="Pauses the music")
		async def cmd_pause(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.pause(ms, ctx)

		@bot.tree.command(name="resume", description="Resumes the paused music")
		async def cmd_resume(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.resume(ms, ctx)

		@bot.tree.command(name="stop", description="Stops the music and leaves the channel")
		async def cmd_stop(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.stop(ms, ctx)

		@bot.tree.command(name="next", description="Skips to the next track")
		async def cmd_next(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.next(ms, ctx)

		@bot.tree.command(name="shuffle", description="Randomizes the track queue")
		async def cmd_shuffle(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.shuffle(ms, ctx)

		@bot.tree.command(name="remove", description="Removes a track from the queue")
		async def cmd_remove(ctx: Interaction, number_in_queue: int):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.remove(ms, ctx, number_in_queue)

		@bot.tree.command(name="goto", description="Jumps to a specific track in the queue")
		async def cmd_goto(ctx: Interaction, number_in_queue: int):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.goto(ms, ctx, number_in_queue)

		@bot.tree.command(name="queue", description="Displays the current track queue")
		async def cmd_queue(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			guild_cmd.queue_list(ms, ctx)

		# @bot.tree.command(name="search_v1", description="Search tracks (old way)")
		# async def cmd_search_v1(ctx: Interaction, input: str, engine: SourceType | None):
		# 	if (await self.__use_on_guild_only(ctx)) is False:
		# 		return
		# 	ms = MessageSenderQueued(ctx)
		# 	await ms.thinking()
		# 	guild: Guild = ctx.guild  # type: ignore
		# 	guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

		# 	await guild_cmd.searchV1(ms, input, engine)

		@bot.tree.command(name="search", description="Searches for tracks")
		async def cmd_search(ctx: Interaction, input: str, engine: SourceType | None):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.search(ms, input, engine)

		@bot.tree.command(
			name="play_url", description="Plays a track, artist, album, or playlist from a URL"
		)
		async def cmd_play_url(ctx: Interaction, url: str):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play_url(ms, ctx, url)

		@bot.tree.command(
			name="play_url_next",
			description="Plays a track, artist, album, or playlist from a URL next in the queue",
		)
		async def cmd_play_url_next(ctx: Interaction, url: str):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			ms = MessageSenderQueued(ctx)
			await ms.thinking()
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play_url(ms, ctx, url, at_end=False)

		# @bot.tree.command(name="spam", description="Test spam")
		# async def cmd_spam(ctx: Interaction):
		# 	ms = MessageSenderQueued(ctx)
		# 	await ms.thinking()

		# 	for i in range(100):
		# 		ms.add_message(f"Spam n°{i}")
		# 	await ctx.response.send_message("Spam ended")

	async def __use_on_guild_only(self, ctx: Interaction) -> bool:
		if ctx.guild is None:
			await ctx.response.send_message("You can use this command only on a guild")
			return False
		return True
