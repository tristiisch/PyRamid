from discord import *
from deezer.downloader import DeezerDownloader
from discord.guild_songs import GuildSongs

from tools.object import GuildData, MessageSender, Track, TrackMinimal


class GuildCmd:

	def __init__(self, guild_data : GuildData, guild_songs : GuildSongs, deezer_dl : DeezerDownloader):
		self.deezer_dl: DeezerDownloader = deezer_dl
		self.guild_data: GuildData = guild_data
		self.guild_songs: GuildSongs = guild_songs

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
		
		self.guild_data.track_list.add_song(track_downloaded)
		await self.guild_songs.goto_channel(voice_channel)
		await self.guild_songs.play(MessageSender(ctx))

	async def stop(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or await self.__verify_bot_channel(ctx, voice_channel):
			return False

		self.guild_data.track_list.clear()
		if await self.guild_songs.exit() == False:
			await ctx.response.send_message("The bot does not currently play music")
			return False

		await ctx.response.send_message("Music stop")
		return True

	async def pause(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or await self.__verify_bot_channel(ctx, voice_channel):
			return False

		if await self.guild_songs.pause() == False:
			await ctx.response.send_message("The bot does not currently play music")
			return False

		await ctx.response.send_message("Music paused")
		return True

	async def resume(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or await self.__verify_bot_channel(ctx, voice_channel):
			return False
	
		if await self.guild_songs.resume() == False:
			await ctx.response.send_message("The bot is not currently paused")
			return False

		await ctx.response.send_message("Music resume")
		return True

	async def next(self, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self.__verify_voice_channel(ctx)
		if not voice_channel or await self.__verify_bot_channel(ctx, voice_channel):
			return False
	
		if await self.guild_songs.stop() == False:
			await ctx.response.send_message("The bot does not currently play music")
			return False
		self.guild_data.track_list.remove_song()
		await self.guild_songs.goto_channel(voice_channel)
		await self.guild_songs.play(MessageSender(ctx))

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

		self.guild_data.track_list.add_songs(tracks)
		await self.guild_songs.goto_channel(voice_channel)
		await self.guild_songs.play(MessageSender(ctx))

	async def __verify_voice_channel(self, ctx: Interaction) -> VoiceChannel | None : 
		user: User | Member = ctx.user

		# only play music if user is in a voice channel
		voice_state: VoiceState | None = user.voice
		if voice_state is None:
			await ctx.response.send_message("You're not in a channel.")
			return

		# grab user's voice channel
		voice_channel: VoiceChannel | None = voice_state.channel
		return voice_channel

	async def __verify_bot_channel(self, ctx: Interaction, channel: VoiceChannel) -> bool :
		vc : VoiceClient = self.guild_data.voice_client

		if (vc.channel.id != channel.id):
			await ctx.response.send_message("You're not in the bot channel.")
			return False
		return True
