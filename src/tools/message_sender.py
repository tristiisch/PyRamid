import tools.utils

from typing import Optional, Sequence
from discord import AllowedMentions, Embed, Interaction
from discord.ui import View
from discord.utils import MISSING

MAX_MSG_LENGTH = 2000


class MessageSender:
	def __init__(self, ctx: Interaction):
		self.ctx = ctx

	async def add_message(
		self,
		content: str = MISSING,
		# *,
		# username: str = MISSING,
		# avatar_url: Any = MISSING,
		# tts: bool = MISSING,
		# ephemeral: bool = MISSING,
		# file: File = MISSING,
		# files: Sequence[File] = MISSING,
		# embed: Embed = MISSING,
		# embeds: Sequence[Embed] = MISSING,
		# allowed_mentions: AllowedMentions = MISSING,
		# view: View = MISSING,
		# thread: Snowflake = MISSING,
		# thread_name: str = MISSING,
		# wait: Literal[True] = True,
		# suppress_embeds: bool = MISSING,
		# silent: bool = MISSING,
	):
		await self.ctx.followup.send(
			content,
			# username=username,
			# avatar_url=avatar_url,
			# tts=tts,
			# ephemeral=ephemeral,
			# file=file,
			# files=files,
			# embed=embed,
			# embeds=embeds,
			# allowed_mentions=allowed_mentions,
			# view=view,
			# thread=thread,
			# thread_name=thread_name,
			# wait=wait,
			# suppress_embeds=suppress_embeds,
			# silent=silent,
		)

	async def response_message(
		self,
		*,
		content: Optional[str] = MISSING,
		embeds: Sequence[Embed] = MISSING,
		embed: Optional[Embed] = MISSING,
		# attachments: Sequence[Union[Attachment, File]] = MISSING,
		view: Optional[View] = MISSING,
		allowed_mentions: Optional[AllowedMentions] = MISSING,
	):
		if content != MISSING and content != "":
			new_content, is_used = tools.utils.substring_with_end_msg(
				content, MAX_MSG_LENGTH, "{} more..."
			)
			if is_used:
				content = new_content

		if self.ctx.response.is_done():
			await self.ctx.edit_original_response(
				content=content,
				embeds=embeds,
				embed=embed,
				view=view,
				allowed_mentions=allowed_mentions,
			)
		else:
			await self.ctx.response.send_message(
				content=content,
				embeds=embeds,
				embed=embed,  # type: ignore
				view=view,  # type: ignore
				allowed_mentions=allowed_mentions,  # type: ignore
			)  # type: ignore

	async def add_code_message(self, content: str, prefix=None, suffix=None):
		max_length = MAX_MSG_LENGTH
		if prefix is None:
			prefix = "```"
		else:
			prefix += "\n```"
		if suffix is None:
			suffix = "```"
		else:
			suffix += "\n```"

		max_length -= len(prefix) + len(suffix)

		substrings_generator = tools.utils.split_string_by_length(content, max_length)

		if not self.ctx.response.is_done():
			first_substring = next(substrings_generator, None)
			if first_substring is not None:
				await self.ctx.response.send_message(content=f"```{first_substring}```")

		for substring in substrings_generator:
			await self.ctx.followup.send(content=f"```{substring}```")
