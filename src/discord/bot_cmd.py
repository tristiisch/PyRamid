import math
import discord

from typing import Callable
from logging import Logger
from discord.user import BaseUser
from discord.ext.commands import Bot
from discord import (
	AppInfo,
	ClientUser,
	Guild,
	Interaction,
)
from discord.guild_cmd import GuildCmd
from tools.environment import Environment
from tools.information import ProgramInformation


class BotCmd:
	def __init__(
		self,
		bot: Bot,
		get_guild_cmd: Callable[[Guild], GuildCmd],
		logger: Logger,
		info: ProgramInformation,
		environment: Environment,
	):
		self.__bot = bot
		self.__get_guild_cmd = get_guild_cmd
		self.__logger = logger
		self.__info = info
		self.__environment = environment

	def register(self):
		bot = self.__bot

		@bot.tree.command(name="ping", description="Get time between Bot and Discord")
		async def cmd_ping(ctx: Interaction):
			await ctx.response.send_message(f"Pong ! ({math.trunc(bot.latency * 1000)}ms)")

		@bot.tree.command(name="about", description="About the bot")
		async def about(ctx: Interaction):
			bot_user: ClientUser | None
			if bot.user is not None:
				bot_user = bot.user
			else:
				bot_user = None
				self.__logger.warning("Unable to get self user instance")

			info = self.__info
			embed = discord.Embed(title=info.name.capitalize(), color=discord.Color.gold())
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

			embed.add_field(name="Version", value=info.get_full_version(), inline=True)
			embed.add_field(name="OS", value=info.os, inline=True)
			embed.add_field(
				name="Environment",
				value=self.__environment.name.capitalize(),
				inline=True,
			)

			await ctx.response.send_message(embed=embed)

		@bot.tree.command(name="play", description="Play a song in the voice channel")
		async def cmd_play(ctx: Interaction, input: str):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play(ctx, input)

		@bot.tree.command(name="pause", description="Pause music")
		async def cmd_pause(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.pause(ctx)

		@bot.tree.command(name="resume", description="Resume music")
		async def cmd_resume(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.resume(ctx)

		@bot.tree.command(name="stop", description="Stop music and exit channel")
		async def cmd_stop(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.stop(ctx)

		@bot.tree.command(name="next", description="Next music")
		async def cmd_next(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.next(ctx)

		@bot.tree.command(name="shuffle", description="Randomize the queue")
		async def cmd_shuffle(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.suffle(ctx)

		@bot.tree.command(name="remove", description="Remove an element in the queue")
		async def cmd_remove(ctx: Interaction, number_in_queue: int):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.remove(ctx, number_in_queue)

		@bot.tree.command(name="goto", description="Go to an element in the queue")
		async def cmd_goto(ctx: Interaction, number_in_queue: int):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.goto(ctx, number_in_queue)

		@bot.tree.command(name="queue", description="List musique in queue")
		async def cmd_queue(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.queue_list(ctx)

		@bot.tree.command(
			name="search",
			description="Search musique",
		)
		async def cmd_search(ctx: Interaction, input: str, engine: str | None):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.search(ctx, input, engine)

		@bot.tree.command(
			name="play_multiple", description="Plays the first 10 songs of the search"
		)
		async def play_multiple(ctx: Interaction, input: str):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play_multiple(ctx, input)

		@bot.tree.command(name="play_url", description="Plays songs by URL from Deezer")
		async def play_url(ctx: Interaction, url: str):
			if (await self.__use_on_guild_only(ctx)) is False:
				return
			guild: Guild = ctx.guild  # type: ignore
			guild_cmd: GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.play_url(ctx, url)

		# @bot.command()
		# async def ignore_none_slash_cmd():
		# 	pass

	async def __use_on_guild_only(self, ctx: Interaction) -> bool:
		if ctx.guild is None:
			await ctx.response.send_message("You can use this command only on a guild")
			return False
		return True
