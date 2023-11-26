import asyncio
from logging import Logger
from threading import Thread

from discord import Interaction, VoiceChannel

import data.tracklist as utils_list_track
from data.guild_data import GuildData
from data.track import TrackMinimal
from connector.discord.guild_cmd_tools import GuildCmdTools
from connector.discord.guild_queue import GuildQueue
from data.functional.messages.message_sender_queued import MessageSenderQueued
from data.functional.engine_source import EngineSource


class GuildCmd(GuildCmdTools):
	def __init__(
		self,
		logger: Logger,
		guild_data: GuildData,
		guild_queue: GuildQueue,
		engine_source: EngineSource,
	):
		self.logger = logger
		self.engine_source = engine_source
		self.data = guild_data
		self.queue = guild_queue

	async def play(self, ms: MessageSenderQueued, ctx: Interaction, input: str, at_end=True) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		ms.edit_message(f"Searching **{input}**", "search")

		track: TrackMinimal | None = self.data.search_engine.default_engine.search_track(input)
		if not track:
			ms.edit_message("**{input}** not found.", "search")
			return False

		return await self._execute_play(ms, voice_channel, track, at_end=at_end)

	async def stop(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		self.data.track_list.clear()
		if await self.queue.exit() is False:
			ms.add_message("The bot does not currently play music")
			return False

		ms.add_message("Music stop")
		return True

	async def pause(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.pause() is False:
			ms.add_message("The bot does not currently play music")
			return False

		ms.add_message("Music paused")
		return True

	async def resume(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.resume() is False:
			ms.add_message("The bot is not currently paused")
			return False

		ms.add_message("Music resume")
		return True

	async def next(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.has_next() is False:
			if self.queue.stop() is False:
				ms.add_message("The bot does not currently play music")
				return False
			else:
				ms.add_message("The bot didn't have next music")
				return True

		await self.queue.goto_channel(voice_channel)
		if self.queue.next() is False:
			ms.add_message("Unable to play next music")
			return False

		ms.add_message("Skip musique")
		return True

	async def suffle(self, ms: MessageSenderQueued, ctx: Interaction):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if not self.queue.shuffle():
			ms.add_message("No need to shuffle the queue.")
			return False

		ms.add_message("The queue has been shuffled.")
		return True

	async def remove(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if number_in_queue <= 0:
			ms.add_message(
				content=f"Unable to remove element with the number {number_in_queue} in the queue"
			)
			return False

		if number_in_queue == 1:
			ms.add_message(
				content="Unable to remove the current track from the queue. Use `next` instead"
			)
			return False

		track_deleted = self.queue.remove(number_in_queue - 1)
		if track_deleted is None:
			ms.add_message(
				content=f"There is no element with the number {number_in_queue} in the queue"
			)
			return False

		ms.add_message(
			content=f"**{track_deleted.get_full_name()}** has been removed from queue"
		)
		return True

	async def goto(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if number_in_queue <= 0:
			ms.add_message(
				content=f"Unable to go to element with number {number_in_queue} in the queue"
			)
			return False

		if number_in_queue == 1:
			ms.add_message(
				content="Unable to remove the current track from the queue. Use `next` instead"
			)
			return False

		tracks_removed = self.queue.goto(number_in_queue - 1)
		if tracks_removed <= 0:
			ms.add_message(
				content=f"There is no element with the number {number_in_queue} in the queue"
			)
			return False

		# +1 for current track
		ms.add_message(f"f{tracks_removed + 1} tracks has been skipped")
		return True

	def queue_list(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		queue: str | None = self.queue.queue_list()
		if queue is None:
			ms.add_message("Queue is empty")
			return False

		ms.add_code_message(queue, prefix="Here's the music in the queue :")
		return True

	def search(
		self, ms: MessageSenderQueued, ctx: Interaction, input: str, engine: str | None
	) -> bool:
		if engine is None:
			search_engine = self.data.search_engine.default_engine
		else:
			test_value = self.data.search_engines.get_engine(engine)
			if not test_value:
				ms.add_message(f"Search engine **{engine}** not found.")
				return False
			else:
				search_engine = test_value

		result: list[TrackMinimal] | None = search_engine.search_tracks(input)

		if not result:
			ms.add_message(f"**{input}** not found.")
			return False

		hsa = utils_list_track.to_str(result)
		ms.add_code_message(hsa, prefix="Here are the results of your search :")
		return True

	async def play_multiple(self, ms: MessageSenderQueued, ctx: Interaction, input: str) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		ms.edit_message(f"Searching **{input}** ...", "search")

		tracks: list[TrackMinimal] | None = self.data.search_engine.default_engine.search_tracks(input)
		if not tracks:
			ms.edit_message(f"**{input}** not found.", "search")
			return False

		return await self._execute_play_multiple(ms, voice_channel, tracks)

	async def play_url(self, ms: MessageSenderQueued, ctx: Interaction, url: str, at_end=True) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user)
		if not voice_channel:
			return False

		ms.edit_message(f"Searching **{url}** ...", "search")

		result: (
			tuple[list[TrackMinimal], list[TrackMinimal]] | TrackMinimal | None
		) = await self.data.search_engine.search_by_url(url)
		if not result:
			ms.edit_message(f"**{url}** not found.", "search")
			return False

		if isinstance(result, tuple):
			tracks, tracks_unfindable = result
			self._informs_unfindable_tracks(ms, tracks_unfindable)
			return await self._execute_play_multiple(ms, voice_channel, tracks, at_end=at_end)
		elif isinstance(result, TrackMinimal):
			tracks = result
			return await self._execute_play(ms, voice_channel, tracks, at_end=at_end)
		else:
			raise Exception("Unknown type 'res'")
