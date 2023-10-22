import math
import traceback
import discord
import logging

from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from discord import Guild, Interaction, PrivilegedIntentsRequired, Role, Status
from typing import Dict, Optional
from deezer_api.downloader import DeezerDownloader
from discord.utils import MISSING
from deezer_api.search import DeezerSearch
from discord.guild_cmd import GuildCmd
from discord.guild_queue import GuildQueue
from spotify.search import SpotifySearch
from tools.config import Config
from tools.information import ProgramInformation
from tools.object import *
from tools.guild_data import GuildData
from tools.abc import ASearch

class DiscordBot:
	def __init__(self, logger: logging.Logger, information: ProgramInformation, config: Config, deezer_dl: DeezerDownloader):
		self.logger = logger
		self.information = information
		self.token = config.discord_token
		self.ffmpeg = config.discord_ffmpeg
		self.deezer_dl = deezer_dl
		self.search_engines: Dict[str, ASearch] = dict({
			"spotify": SpotifySearch(config.spotify_client_id, config.spotify_client_secret),
			"deezer": DeezerSearch()
		})

		intents = discord.Intents.default()
		# intents.members = True
		intents.guilds = True
		intents.message_content = True

		bot = commands.Bot(command_prefix="$$", intents=intents)
		self.bot : commands.Bot  = bot

		self.guilds_instances : Dict[int, GuildInstances] = {}
		

	def create(self):
		self.logger.info(f"Discord bot creating with discord.py v%s ...", discord.__version__)
		bot = self.bot

		@bot.event
		async def on_ready():
			await bot.tree.sync()
			await bot.change_presence(status=Status.online,
							 activity=discord.Activity(type=discord.ActivityType.listening, name=f"{self.information.get_version()}"))
			
			if bot.user == None:
				self.logger.warning(f"Unable to get discord bot name")
			else:
				self.logger.info(f"Discord bot name '{bot.user.name}'")
			self.logger.info("------ GUILDS ------")

			for guild in bot.guilds:
				self.logger.info(f"'{guild.name}' has {guild.member_count} members. Created is {guild.owner}.")

				if bot.user == None:
					self.logger.warning(f"Enable to get discord bot - Unable to get his roles")
				else:
					bot_member = guild.get_member(bot.user.id)
					if bot_member == None:
						self.logger.warning(f"  Enable to get discord bot role on {guild.name}")
					else:
						self.logger.info("  Bot roles :")
						for r in bot_member.roles:
							role: Role = r
							self.logger.info(f"    '{role.name}' ID {role.id}")

				self.logger.info('----------------------')
			self.logger.info(f"Discord bot ready")
			# await client.close()

		@bot.tree.command(name="ping", description="Get time between Bot and Discord")
		async def cmd_ping(ctx: Interaction):
			await ctx.response.send_message(f"Pong ! ({math.trunc(bot.latency * 1000)}ms)")

		# @bot.tree.command(name="vuvuzela", description="Plays an awful vuvuzela in the voice channel")
		# async def cmd_vuvuzela(ctx: Interaction):
		# 	guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
		# 	await guild_cmd.vuvuzela(ctx, input)

		@bot.tree.command(name="play", description="Play a song in the voice channel")
		async def cmd_play(ctx: Interaction, input : str):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.play(ctx, input)

		@bot.tree.command(name="pause", description="Pause music")
		async def cmd_pause(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.pause(ctx)

		@bot.tree.command(name="resume", description="Resume music")
		async def cmd_resume(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.resume(ctx)

		@bot.tree.command(name="stop", description="Stop music and exit channel")
		async def cmd_stop(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.stop(ctx)

		@bot.tree.command(name="next", description="Next music")
		async def cmd_next(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.next(ctx)

		@bot.tree.command(name="queue", description="List musique in queue")
		async def cmd_queue(ctx: Interaction):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.queue_list(ctx)

		@bot.tree.command(name="search", description="Search musique", )
		async def cmd_search(ctx: Interaction, input: str, engine : str | None):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)
			
			await guild_cmd.search(ctx, input, engine)

		@bot.tree.command(name="test", description="Testing things")
		async def cmd_test(ctx: Interaction, input : str):
			if (await self.__use_on_guild_only(ctx)) == False:
				return
			guild: Guild = ctx.guild # type: ignore
			guild_cmd : GuildCmd = self.__get_guild_cmd(guild)

			await guild_cmd.test(ctx, input)

		# @bot.command()
		# async def ignore_none_slash_cmd():
		# 	pass

		@bot.event
		async def on_command_error(ctx, error):
			if isinstance(error, CommandNotFound):
				await ctx.send("That command didn't exists !")
				return
			logging.debug("on_command_error", error)

		@bot.event
		async def on_error(event, *args, **kwargs):
			message = args[0] # Message object
			# traceback.extract_stack
			logging.error(traceback.format_exc())
			# await bot.send_message(message.channel, "You caused an error!")

	def start(self):
		self.logger.info(f"Discord bot starting")
		try:
			self.bot.run(self.token, log_handler=None)
		except PrivilegedIntentsRequired as ex:
			raise ex
		
	async def __use_on_guild_only(self, ctx: Interaction) -> bool:
		if ctx.guild == None:
			await ctx.response.send_message(f"You can use this command only on a guild")
			return False
		return True

	def __get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if not guild.id in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(guild, self.deezer_dl, self.ffmpeg, self.search_engines)

		return self.guilds_instances[guild.id].cmds
	

class GuildInstances:
	def __init__(self, guild : Guild, deezer_downloader : DeezerDownloader, ffmpeg_path : str, search_engines: Dict[str, ASearch]):
		self.data = GuildData(guild, search_engines)
		self.songs = GuildQueue(self.data, ffmpeg_path)
		self.cmds = GuildCmd(self.data, self.songs, deezer_downloader)