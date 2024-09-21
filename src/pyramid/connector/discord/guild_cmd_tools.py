import logging
import traceback
from typing import Union
from discord.abc import Messageable
from discord import Member, StageChannel, TextChannel, User, VoiceChannel, VoiceClient, VoiceState

from pyramid.data.exceptions import DeezerTokenException
from pyramid.api.services.source_service import ISourceService
from pyramid.data.music.track import Track
from pyramid.data.music.track_minimal_deezer import TrackMinimalDeezer
from pyramid.data.music.track_minimal import TrackMinimal
from pyramid.data.guild_data import GuildData
from pyramid.data.tracklist import TrackList
from pyramid.connector.discord.guild_queue import GuildQueue
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued


class GuildCmdTools:
	def __init__(
		self,
		guild_data: GuildData,
		guild_queue: GuildQueue,
		engine_source: ISourceService,
	):
		self.engine_source = engine_source
		self.data = guild_data
		self.queue = guild_queue

	async def _verify_voice_channel(
		self, ms: MessageSenderQueued, user: User | Member, msg_channel: Messageable
	) -> VoiceChannel | None:
		if not isinstance(user, Member):
			raise Exception("Can only be used by a member (user in guild).")

		member: Member = user
		bot: Member = self.data.guild.me

		if not isinstance(msg_channel, TextChannel):
			ms.edit_message("This is not a standard text channel. Please retry in another channel.")
			return None
		txt_channel: TextChannel = msg_channel

		txt_permission = txt_channel.permissions_for(bot)
		if not txt_permission.text:
			ms.edit_message(f"I'm unable to send messages to {txt_channel.mention}. Please ask the administrator to grant me the necessary permissions or disable this command in this channel.")
			return None

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
		if bot.voice and bot.voice.channel:
			current_channel: Union[VoiceChannel, StageChannel] = bot.voice.channel
			if current_channel.id == voice_channel.id:
				return voice_channel

		voice_permissions = voice_channel.permissions_for(bot)
		if not voice_permissions.connect:
			ms.edit_message(f"I can't join {voice_channel.mention}. Please ask the administrator to grant me the necessary permissions or join another channel, redo the command, and then move me to the first channel.")
			return None

		if not voice_permissions.speak:
			ms.add_message(content=f"Warning! I can't speak in {voice_channel.mention}. Please ask the administrator to grant me the necessary permissions.")

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
			try:
				track_downloaded: Track | None = await self.engine_source.download_track(track)
			except DeezerTokenException as err:
				ms.add_message("😥 **There are currently no music accounts available**. Try again later.")
				return False
			except Exception as err:
				ms.add_message("😓 **Unable to connect to music API**. Try again later.")
				return False
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

		try:
			track_downloaded: Track | None = await self.engine_source.download_track(track)
		except DeezerTokenException as err:
			ms.add_message("😥 **There are currently no music accounts available**. Try again later.")
			return False
		except Exception as err:
			ms.add_message("😓 **Unable to connect to music API**. Try again later.")
			return False

		if not track_downloaded:
			ms.add_message(f"ERROR > **{track.get_full_name()}** can't be downloaded.")
			return False

		if (at_end and not tl.add_track(track_downloaded)) or (
			not at_end and not tl.add_track_after(track_downloaded)
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
