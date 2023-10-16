
import asyncio
import sys
import discord

from discord import *
from discord.music_player_interface import *
from tools.object import GuildData, MessageSender, Track, TrackList

class GuildQueue:

	def __init__(self, data : GuildData, ffmpeg_path: str):
		self.data : GuildData = data
		self.ffmpeg = ffmpeg_path
		self.song_end_action = self.__song_end_continue

	def is_playing(self) -> bool:
		return self.data.voice_client.is_playing()

	async def goto_channel(self, channel : VoiceChannel) -> bool:
		vc : VoiceClient = self.data.voice_client

		if vc != None and vc.is_connected():
			if (vc.channel.id != channel.id):
				# Move to an other voice channel
				await self.data.voice_client.move_to(channel)
				return True
		else:
			# Connect into voice channel
			self.data.voice_client = await channel.connect(self_deaf = True)
			return True
		return False

	async def play(self, msg_sender: MessageSender) -> bool:
		tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client
		
		if tl.is_empty():
			raise Exception("Track list is empty")
		
		vc : VoiceClient = self.data.voice_client
		if vc == None:
			raise Exception("Bot is not in a channel")

		if vc.is_playing():
			return False

		if vc.is_paused():
			vc.resume()
			return True

		track : Track = tl.get_song()

		# Prepare codex to play song
		source = discord.FFmpegPCMAudio(track.file_local, executable=self.ffmpeg, stderr = sys.stderr)

		# Play song into discord
		# tl.obs_start()
		vc.play(source, after=lambda err: asyncio.run_coroutine_threadsafe(self.__song_end(err, msg_sender), vc.loop).result())

		# Message in channel with player
		mpi = MusicPlayerInterface()
		await msg_sender.response_message(content=f"", embed = mpi.embed_track(track))

		return True
	
	def stop(self) -> bool:
		# tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client
		if vc == None:
			return False
		if not vc.is_playing():
			return False
		
		self.song_end_action = self.__song_end_stop
		vc.stop()
		# tl.obs_clear()
		return True

	def exit(self) -> bool:
		vc : VoiceClient = self.data.voice_client
		if self.stop() == False:
			return False
		if vc.is_connected():
			vc.disconnect()
			return True
		return False

	def pause(self) -> bool:
		# tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client
		if vc == None:
			return False
		if vc.is_playing():
			vc.pause()
			# tl.obs_pause()
			return True
		return False

	def resume(self) -> bool:
		# tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client
		if vc == None:
			return False
		if vc.is_paused():
			vc.resume()
			# tl.obs_resume()
			return True
		return False

	def has_next(self) -> bool:
		tl : TrackList = self.data.track_list
		return tl.has_next()
	
	def next(self) -> bool:
		# tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client
		if vc == None:
			return False
		if vc.is_playing() or vc.is_paused():
			self.song_end_action = self.__song_end_next
			# tl.obs_clear()
			vc.stop()
			return True
		return False

	def queue_list(self) -> str:
		tl : TrackList = self.data.track_list
		
		queue_list: str = "\n".join([f"n°{i+1}\t{s.author_name} - {s.name} ({s.duration})" for i, s in enumerate(tl.get_songs())])
		return queue_list
	
	# Called after song played
	async def __song_end(self, err: Exception | None, msg_sender: MessageSender):
		if err is not None:
			await msg_sender.add_message(f"An error occurred while playing song: {err}")

		await self.song_end_action(err, msg_sender)
		self.song_end_action = self.__song_end_continue

	async def __song_end_continue(self, err: Exception | None, msg_sender: MessageSender):
		tl : TrackList = self.data.track_list
		vc : VoiceClient = self.data.voice_client

		if tl.is_empty() == False:
			tl.remove_song()

		if tl.is_empty():
			await vc.disconnect()
			await msg_sender.response_message(content = f"Bye bye")
		else:
			await self.play(msg_sender)

	async def __song_end_next(self, err: Exception | None, msg_sender: MessageSender):
		tl : TrackList = self.data.track_list

		if tl.is_empty() == False:
			tl.remove_song()

		if tl.is_empty():
			raise Exception("They is no song to play after")
		await self.play(msg_sender)

	async def __song_end_stop(self, err: Exception | None, msg_sender: MessageSender):
		tl : TrackList = self.data.track_list
		
		tl.clear()
		pass