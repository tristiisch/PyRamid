
import asyncio
import sys
from discord import *
import discord
from tools.object import GuildData, MessageSender, Track, TrackList

class GuildSongs:

	def __init__(self, guild_data : GuildData, ffmpeg_path: str):
		self.guild_data : GuildData = guild_data
		self.ffmpeg = ffmpeg_path

	def is_playing(self) -> bool:
		return self.guild_data.voice_client.is_playing()

	async def goto_channel(self, channel : VoiceChannel) -> bool:
		vc : VoiceClient = self.guild_data.voice_client

		if vc != None and vc.is_connected():
			if (vc.channel.id != channel.id):
				# Move to an other voice channel
				await self.guild_data.voice_client.move_to(channel)
				return True
		else:
			# Connect into voice channel
			self.guild_data.voice_client = await channel.connect(self_deaf = True)
			return True
		return False


	async def play(self, msg_sender: MessageSender) -> bool:
		tl : TrackList = self.guild_data.track_list
		vc : VoiceClient = self.guild_data.voice_client
		
		if tl.is_empty():
			raise Exception("Track list is empty")
		
		vc : VoiceClient = self.guild_data.voice_client
		if vc == None:
			raise Exception("Bot is not in a channel")

		if vc.is_playing():
			return False

		track : Track = tl.get_song()

		# Prepare codex to play song
		source = discord.FFmpegPCMAudio(track.file_local, executable=self.ffmpeg, stderr = sys.stderr)

		# Play song into discord
		vc.play(source, after=lambda err: asyncio.run_coroutine_threadsafe(self.__song_end(err, msg_sender), vc.loop).result())
		# vc.play(source)

		# Message in channel with player
		await msg_sender.edit_message(content=f"", embed = self.__embed_track(track))

		return True
	
	# Called after song played
	async def __song_end(self, err: Exception | None, msg_sender: MessageSender):
		tl : TrackList = self.guild_data.track_list
		vc : VoiceClient = self.guild_data.voice_client

		if err is not None:
			await msg_sender.add_message(f"An error occurred while playing song: {err}")

		tl.remove_song()

		if (tl.is_empty()):
			await vc.disconnect()
			await msg_sender.edit_message(content = f"Bye bye")
		else:
			await self.play(msg_sender)


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

	def __generate_color_sequence(self, percentage) -> str:
		num_total_blocks = 15
		num_blue_blocks = int(percentage / 100 * num_total_blocks)
		num_red_blocks = 1

		blue_blocks = "🟦" * num_blue_blocks
		red_block = "🔴"
		white_blocks = "⬜" * (num_total_blocks - num_blue_blocks - num_red_blocks)

		sequence = blue_blocks + red_block + white_blocks
		return sequence