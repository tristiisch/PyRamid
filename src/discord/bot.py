import math
import discord
import logging

from discord.ext import commands
from discord import *
from typing import Dict
from deezer.downloader import *
from discord.guild_cmd import GuildCmd
from discord.guild_queue import GuildQueue
from tools.object import *

class DiscordBot:
	def __init__(self, token, ffmpeg, deezer_dl):
		self.token = token
		self.ffmpeg = ffmpeg
		self.deezer_dl : DeezerDownloader = deezer_dl

		intents = discord.Intents.default()
		# intents.members = True
		intents.guilds = True
		intents.message_content = True

		bot = commands.Bot(command_prefix="$$", intents=intents)
		self.bot : commands.Bot  = bot

		self.guilds_instances : Dict[int, GuildInstances] = {}
		

	def create(self):
		print(f"Discord v{discord.__version__} bot creating ...")
		bot = self.bot

		@bot.event
		async def on_ready():
			await bot.tree.sync()
			await bot.change_presence(status=Status.do_not_disturb)
			print(f"Discord bot name '{bot.user.name}'")
			print('------ GUILDS ------')

			for guild in bot.guilds:
				print(f"'{guild.name}' has {guild.member_count} members {guild.owner}.")

				bot_member = guild.get_member(bot.user.id)
				print('  Bot roles :')
				for r in bot_member.roles:
					role: Role = r
					print(f"    '{role.name}' ID {role.id}")

				print('----------------------')
			print(f"Discord bot ready")
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
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.play(ctx, input)

		@bot.tree.command(name="pause", description="Pause music")
		async def cmd_pause(ctx: Interaction):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.pause(ctx)

		@bot.tree.command(name="resume", description="Resume music")
		async def cmd_resume(ctx: Interaction):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.resume(ctx)

		@bot.tree.command(name="stop", description="Stop music and exit channel")
		async def cmd_stop(ctx: Interaction):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.stop(ctx)

		@bot.tree.command(name="next", description="Next music")
		async def cmd_next(ctx: Interaction):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.next(ctx)

		@bot.tree.command(name="queue", description="List musique in queue")
		async def cmd_queue(ctx: Interaction):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			
			await guild_cmd.queue_list(ctx)

		@bot.tree.command(name="test", description="Testing things")
		async def cmd_test(ctx: Interaction, input : str):
			guild_cmd : GuildCmd = self.__get_guild_cmd(ctx.guild)
			await guild_cmd.test(ctx, input)

		# @bot.command()
		# async def ignore_none_slash_cmd():
		# 	pass

	def start(self, log_handler: Optional[logging.Handler] = MISSING):
		print(f"Discord v{discord.__version__} bot starting")
		self.bot.run(self.token, log_handler=log_handler)

	def __get_guild_cmd(self, guild: Guild) -> GuildCmd:
		if not guild.id in self.guilds_instances:
			self.guilds_instances[guild.id] = GuildInstances(guild, self.deezer_dl, self.ffmpeg)

		return self.guilds_instances[guild.id].cmds
	

class GuildInstances:
	def __init__(self, guild : Guild, deezer_downloader : DeezerDownloader, ffmpeg_path : str):
		self.data = GuildData(guild)
		self.songs = GuildQueue(self.data, ffmpeg_path)
		self.cmds = GuildCmd(self.data, self.songs, deezer_downloader)