from discord import Member, User, VoiceChannel, VoiceClient, VoiceState

from data.track import Track, TrackMinimal, TrackMinimalDeezer
from data.guild_data import GuildData
from data.tracklist import TrackList
from connector.discord.guild_queue import GuildQueue
from data.functional.messages.message_sender_queued import MessageSenderQueued
from data.functional.engine_source import EngineSource


class GuildCmdTools:
	def __init__(
		self,
		guild_data: GuildData,
		guild_queue: GuildQueue,
		engine_source: EngineSource,
	):
		self.engine_source = engine_source
		self.data = guild_data
		self.queue = guild_queue

	async def _verify_voice_channel(
		self, ms: MessageSenderQueued, user: User | Member
	) -> VoiceChannel | None:
		if not isinstance(user, Member):
			raise Exception("Can be only used by member (user in guild)")

		member: Member = user

		# only play music if user is in a voice channel
		if member.voice is None:
			ms.edit_message("You're not in a channel.")
			return None
		voice_state: VoiceState = member.voice

		# grab member's voice channel
		if voice_state.channel is None:
			return None
		voice_channel: VoiceChannel = voice_state.channel  # type: ignore

		# verify bot's permission on member voice channel
		bot: Member = self.data.guild.me
		permissions = voice_channel.permissions_for(bot)
		if not permissions.connect:
			ms.edit_message(f"I can't go to {voice_channel.mention}")
			return None

		if not permissions.speak:
			ms.add_message(content=f"Warning ! I can't speak in {voice_channel.mention}")

		return voice_channel

	async def _verify_bot_channel(self, ms: MessageSenderQueued, channel: VoiceChannel) -> bool:
		vc: VoiceClient = self.data.voice_client

		if vc.channel.id != channel.id:
			ms.edit_message("You're not in the bot channel.")
			return False
		return True

	def _informs_unfindable_tracks(
		self, ms: MessageSenderQueued, tracks_unfindable: list[TrackMinimal] | None = None
	):
		if tracks_unfindable is not None and len(tracks_unfindable) != 0:
			track_unvailable_names = []
			tracks_unfindable_names = []
			for t in tracks_unfindable:
				if t.available is False:
					track_unvailable_names.append(t.get_full_name())
				else:
					tracks_unfindable_names.append(t.get_full_name())

			len_track_unvailable = len(track_unvailable_names)
			if len_track_unvailable != 0:
				out = "\n* ".join(track_unvailable_names)
				ms.add_message(
					content="%d track%s are currently unavailable (restricted in certain regions or removed):\n* %s"
					% (
						len_track_unvailable,
						"s" if len_track_unvailable != 1 else "",
						out,
					)
				)
			len_tracks_unfindable = len(tracks_unfindable_names)
			if len_tracks_unfindable != 0:
				out = "\n* ".join(tracks_unfindable_names)
				ms.add_message(
					content="Can't find the audio for %d track%s:\n* %s"
					% (
						len_tracks_unfindable,
						"s" if len_tracks_unfindable != 1 else "",
						out,
					)
				)

	async def _execute_play_multiple(
		self,
		ms: MessageSenderQueued,
		voice_channel: VoiceChannel,
		tracks: list[TrackMinimal] | list[TrackMinimalDeezer],
		at_end=True,
	) -> bool:
		tl: TrackList = self.data.track_list

		length = len(tracks)
		ms.edit_message(f"Downloading ... 0/{length}", "download")

		cant_dl = 0
		for i, track in enumerate(tracks):
			track_downloaded: Track | None = await self.engine_source.download_track(track)
			if not track_downloaded:
				ms.add_message(content=f"ERROR > **{track.get_full_name()}** can't be downloaded.")
				cant_dl += 1
				continue
			if at_end is True and not (
				tl.add_track(track_downloaded) or tl.add_track_after(track_downloaded)
			):
				ms.add_message(
					content=f"ERROR > **{track.get_full_name()}** can't be add to the queue."
				)
				cant_dl += 1
				continue
			ms.edit_message(f"Downloading ... {i + 1 - cant_dl}/{length - cant_dl}", "download")
			if i == 0:
				await self.queue.goto_channel(voice_channel)
				await self.queue.play(ms)

		if length == cant_dl:
			ms.edit_message("None of the music could be downloaded", "download")
			return False

		await self.queue.goto_channel(voice_channel)

		if await self.queue.play(ms) is False:
			ms.edit_message(f"**{length}** tracks have been added to the queue", "download")
		return True

	async def _execute_play(
		self, ms: MessageSenderQueued, voice_channel: VoiceChannel, track: TrackMinimal, at_end=True
	) -> bool:
		tl: TrackList = self.data.track_list
		ms.edit_message(f"**{track.get_full_name()}** found ! Downloading ...", "download")

		track_downloaded: Track | None = await self.engine_source.download_track(track)
		if not track_downloaded:
			ms.add_message(f"ERROR > **{track.get_full_name()}** can't be downloaded.")
			return False

		if (at_end is True and not tl.add_track(track_downloaded)) or not tl.add_track_after(
			track_downloaded
		):
			ms.add_message(
				content=f"ERROR > **{track.get_full_name()}** can't be add to the queue."
			)
			return False
		await self.queue.goto_channel(voice_channel)

		if await self.queue.play(ms) is False:
			ms.edit_message(f"**{track.get_full_name()}** is added to the queue", "download")
		else:
			ms.edit_message(f"Playing **{track.get_full_name()}**", "download")
		return True
