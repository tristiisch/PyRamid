import asyncio
import math
import discord
from discord.ext import commands
from discord import *

from deezer_downloader import *

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
		self.bot = bot
		pass

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

		@bot.tree.command(name="vuvuzela", description="Plays an awful vuvuzela in the voice channel")
		async def cmd_vuvuzela(ctx: Interaction):
			voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
			if not voice_channel:
				return
			await ctx.response.send_message(f"Im comming into {voice_channel.name}")
			await self.__play_song(voice_channel, ctx, "songs_test\Vuvuzela.mp3", self.ffmpeg)

		@bot.tree.command(name="play", description="Play a song in the voice channel")
		async def cmd_play(ctx: Interaction, input : str):
			voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
			if not voice_channel:
				return
			
			await ctx.response.send_message(f"Searching **{input}**")
			track_searched : TrackMinimal | None = self.deezer_dl.get_track_by_name(input)
			if not track_searched:
				await ctx.edit_original_response(content=f"**{input}** not found.")
				return
			await ctx.edit_original_response(content=f"**{track_searched.get_full_name()}** found ! Downloading ...")

			track_downloaded : Track | None = self.deezer_dl.dl_track_by_id(track_searched.id)
			await self.__play_song(voice_channel, ctx, track_downloaded.file_local, self.ffmpeg)
			# await ctx.edit_original_response(content=f"Playing **{track_downloaded.get_full_name()}**.")
			await ctx.edit_original_response(content=f"", embed = self.__embed_track(track_downloaded))

		@bot.command()
		async def ignore_none_slash_cmd(ctx: discord.Interaction):
			pass

	def start(self):
		print(f"Discord v{discord.__version__} bot starting")
		self.bot.run(self.token)

	async def __verify_voice_channel(self, ctx: Interaction,) -> VoiceChannel | None : 
		user: User | Member = ctx.user

		# only play music if user is in a voice channel
		voice_state: VoiceState | None = user.voice
		if voice_state is None:
			await ctx.response.send_message("You are not in a channel.")
			return

		# grab user's voice channel
		voice_channel: VoiceChannel | None = voice_state.channel
		return voice_channel

	async def __play_song(self, channel: VoiceChannel, ctx: Interaction, path_to_play: str, ffmpeg):
		# Connect into voice channel
		vc: VoiceClient = await channel.connect()

		# Called after song played
		def song_end(err: Exception | None):
			if err is not None:
				asyncio.run_coroutine_threadsafe(ctx.followup.send(f"An error occurred while playing song: {err}"), vc.loop).result()

			asyncio.run_coroutine_threadsafe(vc.disconnect(), vc.loop).result()
			asyncio.run_coroutine_threadsafe(ctx.edit_original_response(content=f"Bye bye"), vc.loop).result()

		# Prepare codex to play song
		source = discord.FFmpegPCMAudio(path_to_play, executable=ffmpeg)

		# Play song into discord
		vc.play(source, after=song_end)

	def __embed_track(self, track : Track) -> Embed :
		track.actual_seconds = round(track.duration_seconds * 0.75)
		embed = discord.Embed(
			# title=f"{track.authors}",
			title=f"{track.name}",
			description = f"{track.format_duration(track.actual_seconds)} {self.__generate_color_sequence(track.actual_seconds / track.duration_seconds * 100)} {track.duration}",
			color = discord.Color.blue(),
		)
		embed.set_author(name = ", ".join(track.authors), icon_url = track.author_picture)
		embed.set_thumbnail(url = track.album_picture)
		embed.set_footer(text = f"Release {track.date}")

		return embed

	def __generate_color_sequence(self, percentage):
		num_total_blocks = 15
		num_blue_blocks = int(percentage / 100 * num_total_blocks)
		num_red_blocks = 1

		blue_blocks = "🟦" * num_blue_blocks
		red_block = "🔴"
		white_blocks = "⬜" * (num_total_blocks - num_blue_blocks - num_red_blocks)

		sequence = blue_blocks + red_block + white_blocks
		return sequence