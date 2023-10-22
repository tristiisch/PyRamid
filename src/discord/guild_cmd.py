from spotify.search import SpotifySearch
import tools.utils
import tools.format_list

from discord import Interaction, Member, VoiceChannel, VoiceClient, VoiceState
from deezer_api.downloader import DeezerDownloader
from discord.guild_queue import GuildQueue
from tools.object import Track, TrackMinimal
from tools.message_sender import MessageSender
from tools.guild_data import GuildData

class GuildCmd:

	def __init__(self, guild_data : GuildData, guild_queue : GuildQueue, deezer_dl : DeezerDownloader):
		self.deezer_dl: DeezerDownloader = deezer_dl
		self.data: GuildData = guild_data
		self.queue: GuildQueue = guild_queue

	async def play(self, ctx: Interaction, input : str) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel:
			return False
		
		ms = MessageSender(ctx)
		await ms.response_message(content=f"Searching **{input}**")

		track_searched : TrackMinimal | None = self.data.search_engine.search_track(input)
		if not track_searched:
			await ms.response_message(content=f"**{input}** not found.")
			return False
		await ms.response_message(content=f"**{track_searched.get_full_name()}** found ! Downloading ...")

		track_downloaded : Track | None = await self.deezer_dl.dl_track_by_id(track_searched.id)
		if not track_downloaded:
			await ms.response_message(content=f"**{input}** can't be downloaded.")
			return False
		
		self.data.track_list.add_song(track_downloaded)
		await self.queue.goto_channel(voice_channel)
		
		if await self.queue.play(MessageSender(ctx)) == False:
			await ms.response_message(content=f"**{track_searched.get_full_name()}** is added to the queue")
		return True

	async def stop(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or not await self.__verify_bot_channel(ctx, voice_channel):
			return False

		self.data.track_list.clear()
		if (await self.queue.exit()) == False:
			await ctx.response.send_message("The bot does not currently play music")
			return False

		await ctx.response.send_message("Music stop")
		return True

	async def pause(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or not await self.__verify_bot_channel(ctx, voice_channel):
			return False

		if self.queue.pause() == False:
			await ctx.response.send_message("The bot does not currently play music")
			return False

		await ctx.response.send_message("Music paused")
		return True

	async def resume(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or not await self.__verify_bot_channel(ctx, voice_channel):
			return False
	
		if self.queue.resume() == False:
			await ctx.response.send_message("The bot is not currently paused")
			return False

		await ctx.response.send_message("Music resume")
		return True

	async def next(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or not await self.__verify_bot_channel(ctx, voice_channel):
			return False

		if self.queue.has_next() == False:
			if self.queue.stop() == False:
				await ctx.response.send_message("The bot does not currently play music")
				return False
			else:
				await ctx.response.send_message("The bot didn't have next music")
				return True

		await self.queue.goto_channel(voice_channel)
		if self.queue.next() == False:
			await ctx.response.send_message("Unable to play next music")
			return False
		await ctx.response.send_message("Skip musique")
		return True
	
	async def queue_list(self, ctx: Interaction) -> bool:
		queue: str | None = self.queue.queue_list()
		if queue == None:
			await ctx.response.send_message(f"Queue is empty")
			return False

		ms = MessageSender(ctx)
		await ms.add_code_message(queue, prefix="Here's the music in the queue :")
		return True
	
	async def search(self, ctx: Interaction, input: str, engine : str | None) -> bool:
		ms = MessageSender(ctx)

		if engine == None:
			search_engine = self.data.search_engine
		else:
			test_value = self.data.search_engines.get(engine.lower())
			if not test_value:
				await ms.response_message(content=f"Search engine **{engine}** not found.")
				return False
			else:
				search_engine = test_value

		result: list[TrackMinimal] | None = search_engine.search_tracks(input)
		
		if not result:
			await ms.response_message(content=f"**{input}** not found.")
			return False

		hsa = tools.format_list.tracks(result)

		await ms.add_code_message(hsa, prefix="Here are the results of your search :")

		return True

	# async def vuvuzela(self, ctx: Interaction):
	# 	voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
	# 	if not voice_channel:
	# 		return
	# 	await ctx.response.send_message(f"Im comming into {voice_channel.name}")
	# 	await self.__play_song(voice_channel, ctx, "songs_test\Vuvuzela.mp3", self.ffmpeg)

	async def play_multiple(self, ctx: Interaction, input: str):
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel:
			return
		
		ms = MessageSender(ctx)
		await ms.response_message(content = f"Searching **{input}**")
		
		tracks : list[Track] | None = await self.deezer_dl.test(input)
		if not tracks:
			await ms.response_message(content=f"**{input}** not found.")
			return

		self.data.track_list.add_songs(tracks)
		await self.queue.goto_channel(voice_channel)
		await self.queue.play(MessageSender(ctx))

	async def __verify_voice_channel(self, ctx: Interaction) -> VoiceChannel | None :

		if not isinstance(ctx.user, Member):
			raise Exception("Can be only used by member - user in guild")

		user: Member = ctx.user

		# only play music if user is in a voice channel
		if user.voice is None:
			await ctx.response.send_message("You're not in a channel.")
			return
		voice_state: VoiceState = user.voice

		# grab user's voice channel
		voice_channel: VoiceChannel | None = voice_state.channel # type: ignore
		return voice_channel

	async def __verify_bot_channel(self, ctx: Interaction, channel: VoiceChannel) -> bool :
		vc : VoiceClient = self.data.voice_client

		if (vc.channel.id != channel.id):
			await ctx.response.send_message("You're not in the bot channel.")
			return False
		return True
