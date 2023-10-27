from discord import Member, User, VoiceChannel, VoiceClient, VoiceState
from deezer_api.downloader import DeezerDownloader
from discord.guild_queue import GuildQueue
from tools.guild_data import GuildData
from tools.message_sender import MessageSender
from track.track import Track, TrackMinimal


class GuildCmdTools:
	def __init__(
		self,
		guild_data: GuildData,
		guild_queue: GuildQueue,
		deezer_dl: DeezerDownloader,
	):
		self.deezer_dl = deezer_dl
		self.data = guild_data
		self.queue = guild_queue

	async def _verify_voice_channel(
		self, ms: MessageSender, user: User | Member
	) -> VoiceChannel | None:
		if not isinstance(user, Member):
			raise Exception("Can be only used by member (user in guild)")

		member: Member = user

		# only play music if user is in a voice channel
		if member.voice is None:
			await ms.response_message(content="You're not in a channel.")
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
			await ms.response_message(content=f"I can't go to {voice_channel.mention}")
			return None

		if not permissions.speak:
			await ms.add_message(content=f"Warning ! I can't speak in {voice_channel.mention}")

		return voice_channel

	async def _verify_bot_channel(self, ms: MessageSender, channel: VoiceChannel) -> bool:
		vc: VoiceClient = self.data.voice_client

		if vc.channel.id != channel.id:
			await ms.response_message(content="You're not in the bot channel.")
			return False
		return True

	async def _execute_play_multiple(
		self, ms: MessageSender, voice_channel: VoiceChannel, tracks: list[TrackMinimal], tracks_unfindable: list[TrackMinimal] | None = None
	) -> bool:
		
		if tracks_unfindable is not None and len(tracks_unfindable) != 0:
			track_unvailable_names = []
			tracks_unfindable_names = []
			for t in tracks_unfindable:
				if not t.available:
					track_unvailable_names.append(t.get_full_name())
				else:
					tracks_unfindable_names.append(t.get_full_name())

			if len(track_unvailable_names) != 0:
				out = '\n* '.join(track_unvailable_names)
				await ms.add_message(content=f"These tracks are currently unavailable (restricted in certain regions or removed):\n* {out}")
			if len(tracks_unfindable_names) != 0:
				out = '\n* '.join(tracks_unfindable_names)
				await ms.add_message(content=f"Can't find the audio for this track:\n* {out}")

		length = len(tracks)
		await ms.response_message(content=f"Downloading ... 0/{length}")

		cant_dl = 0
		for i, track in enumerate(tracks):
			track_downloaded: Track | None = await self.deezer_dl.dl_track_by_id(track.id)
			if not track_downloaded:
				await ms.add_message(content=f"**{track.get_full_name()}** can't be downloaded.")
				cant_dl += 1
				continue
			if not self.data.track_list.add_song(track_downloaded):
				await ms.add_message(
					content=f"**{track.get_full_name()}** can't be add to the queue."
				)
				cant_dl += 1
				continue
			await ms.response_message(
				content=f"Downloading ... {i + 1 - cant_dl}/{length - cant_dl}"
			)
			if i == 0:
				await self.queue.goto_channel(voice_channel)
				await self.queue.play(ms)

		if length == cant_dl:
			await ms.response_message(content="None of the music could be downloaded")
			return False

		await self.queue.goto_channel(voice_channel)

		if await self.queue.play(ms) is False:
			await ms.response_message(content=f"**{length}** tracks have been added to the queue")
		return True

	async def _execute_play(
		self, ms: MessageSender, voice_channel: VoiceChannel, track: TrackMinimal
	) -> bool:
		await ms.response_message(content=f"**{track.get_full_name()}** found ! Downloading ...")

		track_downloaded: Track | None = await self.deezer_dl.dl_track_by_id(track.id)
		if not track_downloaded:
			await ms.response_message(content=f"**{track.get_full_name()}** can't be downloaded.")
			return False

		if not self.data.track_list.add_song(track_downloaded):
			await ms.add_message(content=f"**{track.get_full_name()}** can't be add to the queue.")
			return False
		await self.queue.goto_channel(voice_channel)

		if await self.queue.play(ms) is False:
			await ms.response_message(content=f"**{track.get_full_name()}** is added to the queue")
		else:
			await ms.response_message(content=f"Playing **{track.get_full_name()}**")
		return True
