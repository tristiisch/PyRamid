import logging
import tools.utils

from typing import Optional, Sequence
from discord import AllowedMentions, Embed, Interaction, Message, TextChannel, WebhookMessage
from discord.ui import View
from discord.utils import MISSING
from discord.errors import HTTPException

MAX_MSG_LENGTH = 2000


class MessageSender:
	def __init__(self, ctx: Interaction):
		self.__ctx = ctx
		if ctx.channel is None:
			raise NotImplementedError("Unable to create a MessageSender without channel")
		if not isinstance(ctx.channel, TextChannel):
			raise NotImplementedError("Unable to create a MessageSender without text channel")
		self.txt_channel: TextChannel = ctx.channel
		self.last_reponse: Message | WebhookMessage | None = None

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
		if content != MISSING and content != "":
			new_content, is_used = tools.utils.substring_with_end_msg(
				content, MAX_MSG_LENGTH, "{} more characters..."
			)
			if is_used:
				content = new_content

		if not self.__ctx.response.is_done():
			msg = await self.txt_channel.send(content)
		else:
			msg = await self.__ctx.followup.send(
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
				wait=True,
				# suppress_embeds=suppress_embeds,
				# silent=silent,
			)
		return msg

	async def response_message(
		self,
		content: str = MISSING,
		# *,
		# embeds: Sequence[Embed] = MISSING,
		# embed: Optional[Embed] = MISSING,
		# attachments: Sequence[Union[Attachment, File]] = MISSING,
		# view: Optional[View] = MISSING,
		# allowed_mentions: Optional[AllowedMentions] = MISSING,
	):
		if content != MISSING and content != "":
			new_content, is_used = tools.utils.substring_with_end_msg(
				content, MAX_MSG_LENGTH, "{} more characters..."
			)
			if is_used:
				content = new_content

		if self.last_reponse is not None:
			self.last_reponse.edit(content=content)

		elif self.__ctx.response.is_done():
			try:
				await self.__ctx.edit_original_response(
					content=content,
					# embeds=embeds,
					# embed=embed,
					# view=view,
					# allowed_mentions=allowed_mentions,
				)
			except HTTPException as err:
				if err.code == 50027: # 401 Unauthorized : Invalid Webhook Token
					logging.warning("Unable to modify original response, send message instead", exc_info=True)
					self.last_reponse = await self.add_message(content)
				else:
					raise err
		else:
			await self.__ctx.response.send_message(
				content=content,
				# embeds=embeds,
				# embed=embed,  # type: ignore
				# view=view,  # type: ignore
				# allowed_mentions=allowed_mentions,  # type: ignore
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

		if not self.__ctx.response.is_done():
			first_substring = next(substrings_generator, None)
			if first_substring is not None:
				await self.__ctx.response.send_message(content=f"```{first_substring}```")

		for substring in substrings_generator:
			await self.__ctx.followup.send(content=f"```{substring}```")
