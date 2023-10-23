from logging import Logger
from discord.guild_cmd_tools import GuildCmdTools
import tools.utils
import tools.format_list

from discord import Interaction, VoiceChannel
from deezer_api.downloader import DeezerDownloader
from discord.guild_queue import GuildQueue
from tools.object import TrackMinimal
from tools.message_sender import MessageSender
from tools.guild_data import GuildData


class GuildCmd(GuildCmdTools):
	def __init__(
		self,
		logger: Logger,
		guild_data: GuildData,
		guild_queue: GuildQueue,
		deezer_dl: DeezerDownloader,
	):
		self.logger = logger
		self.deezer_dl = deezer_dl
		self.data = guild_data
		self.queue = guild_queue

	async def play(self, ctx: Interaction, input: str) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		await ms.response_message(content=f"Searching **{input}**")

		track: TrackMinimal | None = self.data.search_engine.search_track(input)
		if not track:
			await ms.response_message(content=f"**{input}** not found.")
			return False
		return await self._execute_play(ms, voice_channel, track)

	async def stop(self, ctx: Interaction) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		self.data.track_list.clear()
		if await self.queue.exit() is False:
			await ms.response_message(content="The bot does not currently play music")
			return False

		await ms.response_message(content="Music stop")
		return True

	async def pause(self, ctx: Interaction) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.pause() is False:
			await ms.response_message(content="The bot does not currently play music")
			return False

		await ms.response_message(content="Music paused")
		return True

	async def resume(self, ctx: Interaction) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.resume() is False:
			await ms.response_message(content="The bot is not currently paused")
			return False

		await ms.response_message(content="Music resume")
		return True

	async def next(self, ctx: Interaction) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.has_next() is False:
			if self.queue.stop() is False:
				await ms.response_message(content="The bot does not currently play music")
				return False
			else:
				await ms.response_message(content="The bot didn't have next music")
				return True

		await self.queue.goto_channel(voice_channel)
		if self.queue.next() is False:
			await ms.response_message(content="Unable to play next music")
			return False

		await ms.response_message(content="Skip musique")
		return True

	async def queue_list(self, ctx: Interaction) -> bool:
		ms = MessageSender(ctx)
		queue: str | None = self.queue.queue_list()
		if queue is None:
			await ms.response_message(content="Queue is empty")
			return False

		await ms.add_code_message(queue, prefix="Here's the music in the queue :")
		return True

	async def search(self, ctx: Interaction, input: str, engine: str | None) -> bool:
		ms = MessageSender(ctx)

		if engine is None:
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
	# 	await ms.response_message(content=f"Im comming into {voice_channel.name}")
	# 	await self.__play_song(voice_channel, ctx, "songs_test\Vuvuzela.mp3", self.ffmpeg)

	async def play_multiple(self, ctx: Interaction, input: str) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		await ms.response_message(content=f"Searching **{input}**")

		tracks: list[TrackMinimal] | None = self.data.search_engine.search_tracks(input)
		if not tracks:
			await ms.response_message(content=f"**{input}** not found.")
			return False

		return await self._execute_play_multiple(ms, voice_channel, tracks)

	async def play_url(self, ctx: Interaction, url: str) -> bool:
		ms = MessageSender(ctx)
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		ms = MessageSender(ctx)
		await ms.response_message(content=f"Searching **{url}**")

		tracks: list[TrackMinimal] | TrackMinimal | None = self.data.search_engine.get_by_url(url)
		if not tracks:
			await ms.response_message(content=f"**{url}** not found.")
			return False

		if isinstance(tracks, TrackMinimal):
			return await self._execute_play(ms, voice_channel, tracks)
		else:
			return await self._execute_play_multiple(ms, voice_channel, tracks)
