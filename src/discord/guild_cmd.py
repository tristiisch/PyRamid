from discord import Interaction, Member, VoiceChannel, VoiceClient, VoiceState
from deezer.downloader import DeezerDownloader
from discord.guild_queue import GuildQueue

from tools.object import GuildData, MessageSender, Track, TrackMinimal


class GuildCmd:

	def __init__(self, guild_data : GuildData, guild_queue : GuildQueue, deezer_dl : DeezerDownloader):
		self.deezer_dl: DeezerDownloader = deezer_dl
		self.data: GuildData = guild_data
		self.queue: GuildQueue = guild_queue

	async def play(self, ctx: Interaction, input : str):
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel:
			return
		
		await ctx.response.send_message(f"Searching **{input}**")
		track_searched : TrackMinimal | None = self.deezer_dl.get_track_by_name(input)
		if not track_searched:
			await ctx.edit_original_response(content=f"**{input}** not found.")
			return
		await ctx.edit_original_response(content=f"**{track_searched.get_full_name()}** found ! Downloading ...")

		track_downloaded : Track | None = await self.deezer_dl.dl_track_by_id(track_searched.id)
		
		self.data.track_list.add_song(track_downloaded)
		await self.queue.goto_channel(voice_channel)
		
		if await self.queue.play(MessageSender(ctx)) == False:
			await ctx.edit_original_response(content=f"**{track_searched.get_full_name()}** is added to the queue")

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
	
	async def queue_list(self, ctx: Interaction):
		queue: str = self.queue.queue_list()
		if len(queue) == 0:
			await ctx.response.send_message(f"Queue is empty")
			return False

		await ctx.response.send_message(f"```{queue}```")
		return True

	# async def vuvuzela(self, ctx: Interaction):
	# 	voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
	# 	if not voice_channel:
	# 		return
	# 	await ctx.response.send_message(f"Im comming into {voice_channel.name}")
	# 	await self.__play_song(voice_channel, ctx, "songs_test\Vuvuzela.mp3", self.ffmpeg)

	async def test(self, ctx: Interaction, input: str):
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel:
			return
		
		await ctx.response.send_message(f"Searching **{input}**")
		
		tracks : list[Track] | None = await self.deezer_dl.test(input)
		if not tracks:
			await ctx.edit_original_response(content=f"**{input}** not found.")
			return
		# await ctx.edit_original_response(content=f"**{input}** found ! Downloading ...")

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
