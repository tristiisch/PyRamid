from logging import Logger

from discord import Interaction, Member, User, VoiceChannel
import discord

from pyramid.data import tracklist as utils_list_track
from pyramid.data.guild_data import GuildData
from pyramid.data.track import TrackMinimal
from pyramid.connector.discord.guild_cmd_tools import GuildCmdTools
from pyramid.connector.discord.guild_queue import GuildQueue
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.functional.engine_source import EngineSource, SourceType
from pyramid.data.exceptions import DiscordMessageException
from pyramid.data.a_guild_cmd import AGuildCmd
from pyramid.data.select_view import SelectView


class GuildCmd(AGuildCmd, GuildCmdTools):
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

	async def play(
		self,
		ms: MessageSenderQueued,
		ctx: Interaction,
		input: str,
		engine: SourceType | None,
		at_end=True,
	) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel:
			return False

		ms.edit_message(f"Searching **{input}**", "search")

		try:
			track: TrackMinimal | None = await self.data.search_engine.search_track(input, engine)
		except DiscordMessageException as err:
			ms.edit_message(err.msg, "search")
			return False

		return await self._execute_play(ms, voice_channel, track, at_end=at_end)

	async def stop(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		ctx.channel
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		self.data.track_list.clear()
		if await self.queue.exit() is False:
			ms.add_message("The bot does not currently play music")
			return False

		ms.add_message("Music stop")
		return True

	async def pause(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.pause() is False:
			ms.add_message("The bot does not currently play music")
			return False

		ms.add_message("Music paused")
		return True

	async def resume(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if self.queue.resume() is False:
			ms.add_message("The bot is not currently paused")
			return False

		ms.add_message("Music resume")
		return True

	async def resume_or_pause(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if not self.queue.is_playing():
			await self.resume(ms, ctx)
		else:
			await self.pause(ms, ctx)
		return True

	async def next(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
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

	async def shuffle(self, ms: MessageSenderQueued, ctx: Interaction):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel or not await self._verify_bot_channel(ms, voice_channel):
			return False

		if not self.queue.shuffle():
			ms.add_message("No need to shuffle the queue.")
			return False

		ms.add_message("The queue has been shuffled.")
		return True

	async def remove(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
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

		ms.add_message(content=f"**{track_deleted.get_full_name()}** has been removed from queue")
		return True

	async def goto(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
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

	async def searchV1(
		self, ms: MessageSenderQueued, input: str, engine: SourceType | None = None
	) -> bool:
		try:
			tracks, tracks_unfindable = await self.data.search_engine.search_tracks(input, engine)
		except DiscordMessageException as err:
			ms.add_message(err.msg)
			return False

		hsa = utils_list_track.to_str(tracks)
		if tracks_unfindable:
			hsa = utils_list_track.to_str(tracks_unfindable)
			ms.add_code_message(hsa, prefix=":warning: Can't find the audio for these tracks :")
		ms.add_code_message(hsa, prefix="Here are the results of your search :")
		return True

	async def search(
		self, ms: MessageSenderQueued, input: str, engine: SourceType | None = None
	) -> bool:
		try:
			tracks, tracks_unfindable = await self.data.search_engine.search_tracks(
				input, engine, 25
			)
		except DiscordMessageException as err:
			ms.add_message(err.msg)
			return False

		view = SelectView({
			track: discord.SelectOption(label=track.name, description=f"{track.author_name} - {track.album_title}")
			for track in tracks
		})
		async def callback(user: User | Member, ms: MessageSenderQueued, t: TrackMinimal):
			voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, user, ms.txt_channel)
			if not voice_channel:
				return
			await self._execute_play(ms, voice_channel, t)
		view.on_select = callback

		if tracks_unfindable:
			hsa = utils_list_track.to_str(tracks_unfindable)
			ms.add_code_message(hsa, prefix=":warning: Can't find the audio for these tracks :")
		await ms.ctx.followup.send(content="Choose a title from the provided list :", view=view)
		return True

	async def play_url(
		self, ms: MessageSenderQueued, ctx: Interaction, url: str, at_end=True
	) -> bool:
		voice_channel: VoiceChannel | None = await self._verify_voice_channel(ms, ctx.user, ms.txt_channel)
		if not voice_channel:
			return False

		ms.edit_message(f"Searching **{url}** ...", "search")

		try:
			result = await self.data.search_engine.search_by_url(url)
		except DiscordMessageException as err:
			ms.edit_message(err.msg, "search")
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
