import logging
import discord

from discord import Embed, Locale, Message, TextChannel
from tools.object import Track


class MusicPlayerInterface:
	def __init__(self, locale: Locale):
		self.locale = locale
		self.last_message: Message | None = None

	async def send_player(self, txt_channel: TextChannel, track: Track):
		embed = self.__embed_track(track)

		if self.last_message is not None:
			if txt_channel.last_message_id == self.last_message.id:
				self.last_message = await self.last_message.edit(content="", embed=embed)
				return
			else:
				await self.last_message.delete()
				# await self.last_message.edit(content="", suppress=True)
		self.last_message = await txt_channel.send(content="", embed=embed)

	def __embed_track(self, track: Track) -> Embed:
		# track.actual_seconds = round(track.duration_seconds * 0.75)
		track.actual_seconds = int(0)
		embed = discord.Embed(
			# title=f"{track.authors}",
			title=f"{track.name}",
			description=f"{track.format_duration(track.actual_seconds)} {self.__generate_color_sequence(track.actual_seconds / track.duration_seconds * 100)} {track.duration}",
			color=discord.Color.blue(),
		)
		embed.set_author(name=", ".join(track.authors), icon_url=track.author_picture)
		embed.set_thumbnail(url=track.album_picture)
		embed.set_footer(text=f"Release {track.get_date(self.locale.value)}")

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
