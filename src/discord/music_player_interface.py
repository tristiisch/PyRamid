import discord

from discord import Embed, Locale
from tools.object import Track


class MusicPlayerInterface:
	def __init__(self):
		pass

	def embed_track(self, track: Track, locale: Locale) -> Embed:
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
		embed.set_footer(text=f"Release {track.get_date(locale.value)}")

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
