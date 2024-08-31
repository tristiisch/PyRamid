import discord
from discord import ButtonStyle, Embed, Interaction, Locale, Message
from discord.abc import Messageable
from discord.ui import Button

from pyramid.data.exceptions import MissingPermissionException
from pyramid.data.track import Track
from pyramid.data.tracklist import TrackList
from pyramid.data.a_guild_cmd import AGuildCmd
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued


class PlayerButton(discord.ui.View):
	def __init__(self, queue_action: AGuildCmd, timeout: float | None = 180):
		super().__init__(timeout=timeout)
		self.queue_action = queue_action

	@discord.ui.button(emoji="⏯️", style=ButtonStyle.primary)
	async def next_play_or_pause(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.resume_or_pause(ms, ctx)

	@discord.ui.button(emoji="⏭️", style=ButtonStyle.primary)
	async def next_track(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.next(ms, ctx)

	@discord.ui.button(emoji="🔀", style=ButtonStyle.primary)
	async def shuffle_queue(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.shuffle(ms, ctx)

	@discord.ui.button(emoji="⏹️", style=ButtonStyle.primary)
	async def stop_queue(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.stop(ms, ctx)


class MusicPlayerInterface:
	def __init__(self, locale: Locale, track_list: TrackList):
		self.locale = locale
		self.last_message: Message | None = None
		self.track_list = track_list

	def set_queue_action(self, queue_action: AGuildCmd):
		self.queue_action = queue_action

	async def send_player(self, txt_channel: Messageable, track: Track, locale: Locale):
		embed = self.__embed_track(track, locale)

		last_channel_message = None
		history = txt_channel.history(limit=1)
		try:
			async for message in history:
				last_channel_message = message
		except discord.errors.Forbidden:
			raise MissingPermissionException(discord.Permissions.read_message_history)

		if last_channel_message and self.last_message is not None:
			if last_channel_message.id == self.last_message.id:
				self.last_message = await last_channel_message.edit(content="", embed=embed)
				return
			else:
				await self.last_message.delete()
		self.last_message = await txt_channel.send(
			content="", embed=embed, view=PlayerButton(self.queue_action)
		)

	def __embed_track(self, track: Track, locale: Locale) -> Embed:
		# track.actual_seconds = round(track.duration_seconds * 0.75)
		track.actual_seconds = int(0)
		progress_bar = f"{track.format_duration(track.actual_seconds)} {self.__generate_color_sequence(track.actual_seconds / track.duration_seconds * 100)} {track.duration}"

		embed = discord.Embed(
			# title=f"{track.authors}",
			title=f"{track.name}",
			description=f"{progress_bar}",
			color=discord.Color.blue(),
		)
		embed.add_field(name="Album", value=track.album_title)
		embed.add_field(name="Release", value=track.get_date(locale.value))

		embed.set_author(name=", ".join(track.authors), icon_url=track.author_picture)
		embed.set_thumbnail(url=track.album_picture)
		embed.set_footer(text=f"{self.track_list.get_length()} | {self.track_list.get_duration()}")

		return embed

	def __generate_color_sequence(self, percentage) -> str:
		num_total_blocks = 15
		num_blue_blocks = int(percentage / 100 * num_total_blocks)
		num_red_blocks = 1

		blue_blocks = "🟦" * num_blue_blocks
		red_block = "🔴"
		white_blocks = "⬜" * (num_total_blocks - num_blue_blocks - num_red_blocks)

		sequence = blue_blocks + red_block + white_blocks
		return sequence
