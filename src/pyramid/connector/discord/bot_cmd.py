import math
from logging import Logger
import time
from typing import Callable, List

from discord import AppInfo, ClientUser, Color, Embed, Guild, Interaction
from discord.app_commands import Command
from discord.ext.commands import Bot
from discord.user import BaseUser
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.data.environment import Environment
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.functional.engine_source import SourceType
import pyramid.tools.utils as tools


class BotCmd:
	def __init__(
		self,
		bot: Bot,
		get_guild_cmd: Callable[[Guild], GuildCmd],
		logger: Logger,
		info: ApplicationInfo,
		environment: Environment,
		started: float,
	):
		self.__bot = bot
		self.__get_guild_cmd = get_guild_cmd
		self.__logger = logger
		self.__info = info
		self.__environment = environment
		self.__started = started

	def register(self):
		bot = self.__bot

		@bot.tree.command(
			name="ping", description="Shows the response time between the bot and Discord API"
		)
		async def cmd_ping(ctx: Interaction):
			await ctx.response.defer(thinking=True)
			await ctx.followup.send(f"Pong ! ({math.trunc(bot.latency * 1000)}ms)")

		@bot.tree.command(name="about", description="Information about the bot")
		async def cmd_about(ctx: Interaction):
			await ctx.response.defer(thinking=True)
			bot_user: ClientUser | None
			if bot.user is not None:
				bot_user = bot.user
			else:
				bot_user = None
				self.__logger.warning("Unable to get self user instance")

			info = self.__info
			embed = Embed(title=info.get_name(), color=Color.gold())
			if bot_user is not None and bot_user.avatar is not None:
				embed.set_thumbnail(url=bot_user.avatar.url)

			owner_id: int | None = bot.owner_id
			if owner_id is None and bot.owner_ids is not None and len(bot.owner_ids) > 0:
				owner_id = next(iter(bot.owner_ids))
			else:
				owner_id = None

			owner: BaseUser | None
			if owner_id is not None:
				owner = await bot.fetch_user(owner_id)
			else:
				owner = None

			if owner is None:
				t: AppInfo = await bot.application_info()
				if t.team is not None:
					team = t.team
					if team.owner is not None:
						owner = team.owner

			if owner is not None:
				embed.set_footer(
					text=f"Owned by {owner.display_name}",
					icon_url=owner.avatar.url if owner.avatar is not None else None,
				)

			embed.add_field(name="Version", value=info.get_version(), inline=True)
			embed.add_field(name="OS", value=info.get_os(), inline=True)
			embed.add_field(
				name="Environment",
				value=self.__environment.name.capitalize(),
				inline=True,
			)
			embed.add_field(
				name="Uptime",
				value=tools.time_to_duration(int(round(time.time() - self.__started))),
				inline=True,
			)

			await ctx.followup.send(embed=embed)

		@bot.tree.command(name="help", description="List all commands")
		async def cmd_help(ctx: Interaction):
			await ctx.response.defer(thinking=True)
			all_commands: List[Command] = bot.tree.get_commands()  # type: ignore
			commands_dict = {command.name: command.description for command in all_commands}
			embed_template = Embed(title="List of every commands available", color=Color.gold())
			max_embed = 10
			max_fields = 25
			embeds = []

			for command, description in commands_dict.items():
				embed_template.add_field(name=command, value=description, inline=True)
				if len(embed_template.fields) == max_fields:
					embeds.append(embeds)
					embed_template.clear_fields()

			# Append the last embed if it's not empty
			if len(embed_template.fields) > 0:
				embeds.append(embed_template)

			# Sending the first embed as a response and subsequent follow-up embeds
			for i in range(0, len(embeds), max_embed):
				embeds_chunk = embeds[i : i + max_embed]
				await ctx.followup.send(embeds=embeds_chunk)

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
