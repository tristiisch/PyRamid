import math
import traceback
import logging
import discord

from typing import Dict
from logging import Logger
from discord.ext import commands
from discord.user import BaseUser
from discord.ext.commands.errors import CommandNotFound
from discord import (
	AppInfo,
	ClientUser,
	Guild,
	Interaction,
	PrivilegedIntentsRequired,
	Role,
	Status,
)
from deezer_api.downloader import DeezerDownloader
from deezer_api.search import DeezerSearch
from spotify.search import SpotifySearch
from discord.guild_cmd import GuildCmd
from discord.guild_queue import GuildQueue
from tools.config import Config
from tools.information import ProgramInformation
from tools.guild_data import GuildData
from tools.abc import ASearch
from tools.utils import Mode


class DiscordBot:
	def __init__(
		self,
		logger: logging.Logger,
		information: ProgramInformation,
		config: Config,
		deezer_dl: DeezerDownloader,
	):
		self.logger = logger
		self.information = information
		self.token = config.discord_token
		self.ffmpeg = config.discord_ffmpeg
		self.environment: Mode = config.mode
		self.deezer_dl = deezer_dl
		self.search_engines: Dict[str, ASearch] = dict(
			{
				"spotify": SpotifySearch(config.spotify_client_id, config.spotify_client_secret),
				"deezer": DeezerSearch(),
			}
		)

		intents = discord.Intents.default()
		# intents.members = True
		intents.message_content = True

		bot = commands.Bot(command_prefix="$$", intents=intents)
		self.bot: commands.Bot = bot

		self.guilds_instances: Dict[int, GuildInstances] = {}

	def create(self):
		self.logger.info("Discord bot creating with discord.py v%s ...", discord.__version__)
		bot = self.bot

		@bot.event
		async def on_ready():
			await bot.tree.sync()
			await bot.change_presence(
				status=Status.online,
				activity=discord.Activity(
					type=discord.ActivityType.listening,
					name=f"{self.information.get_version()}",
				),
			)

			if bot.user is None:
				self.logger.warning("Unable to get discord bot name")
			else:
				self.logger.info("Discord bot name '%s'", bot.user.name)
			self.logger.info("------ GUILDS ------")

			for guild in bot.guilds:
				self.logger.info(
					"'%s' has %d members. Created is %s.",
					guild.name,
					guild.member_count,
					guild.owner,
				)

				if bot.user is None:
					self.logger.warning("Enable to get discord bot - Unable to get his roles")
				else:
					bot_member = guild.get_member(bot.user.id)
					if bot_member is None:
						self.logger.warning("  Enable to get discord bot role on %s", guild.name)
					else:
						self.logger.info("  Bot roles :")
						for r in bot_member.roles:
							role: Role = r
							self.logger.info("    '%s' ID %s", role.name, role.id)

				self.logger.info("----------------------")
			self.logger.info("Discord bot ready")
			# await client.close()

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
				self.logger.warning("Unable to get self user instance")

			info = self.information
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
				value=self.environment.name.capitalize(),
				inline=True,
			)

			await ctx.response.send_message(embed=embed)

		# @bot.tree.command(name="vuvuzela", description="Plays an awful vuvuzela in the voice channel")
		# async def cmd_vuvuzela(ctx: Interaction):
		# 	guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
		# 	await guild_cmd.vuvuzela(ctx, input)

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

		@bot.event
		async def on_command_error(ctx, error):
			if isinstance(error, CommandNotFound):
				await ctx.send("That command didn't exists !")
				return
			logging.debug("on_command_error %s", error)

		@bot.event
		async def on_error(event, *args, **kwargs):
			# message = args[0] # Message object
			# traceback.extract_stack
			logging.error("on_error %s", traceback.format_exc())
			# await bot.send_message(message.channel, "You caused an error!")

	def start(self):
		self.logger.info("Discord bot starting")
		try:
			self.bot.run(self.token, log_handler=None)
		except PrivilegedIntentsRequired as ex:
			raise ex

	async def __use_on_guild_only(self, ctx: Interaction) -> bool:
		if ctx.guild is None:
			await ctx.response.send_message("You can use this command only on a guild")
			return False
		return True

	def __get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if guild.id not in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(
				guild,
				self.logger.getChild(guild.name),
				self.deezer_dl,
				self.ffmpeg,
				self.search_engines,
			)

		return self.guilds_instances[guild.id].cmds


class GuildInstances:
	def __init__(
		self,
		guild: Guild,
		logger: Logger,
		deezer_downloader: DeezerDownloader,
		ffmpeg_path: str,
		search_engines: Dict[str, ASearch],
	):
		self.data = GuildData(guild, search_engines)
		self.songs = GuildQueue(self.data, ffmpeg_path)
		self.cmds = GuildCmd(logger, self.data, self.songs, deezer_downloader)
