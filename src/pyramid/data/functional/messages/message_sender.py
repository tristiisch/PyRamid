import asyncio

import tools.utils as tools
from discord import Interaction, Message, WebhookMessage
from discord.utils import MISSING
from discord.abc import Messageable

MAX_MSG_LENGTH = 2000


class MessageSender:
	def __init__(self, ctx: Interaction):
		self.ctx = ctx
		if ctx.channel is None:
			raise NotImplementedError("Unable to create a MessageSender without channel")
		if not isinstance(ctx.channel, Messageable):
			raise NotImplementedError("Unable to create a MessageSender without text channel")
		self.txt_channel: Messageable = ctx.channel
		self.last_message: Message | WebhookMessage | None = None
		self.last_message_surname: dict[str, Message | WebhookMessage] = dict()
		self.loop: asyncio.AbstractEventLoop = ctx.client.loop
		self.think = False

	async def thinking(self):
		await self.ctx.response.defer(thinking=True)
		self.think = True

	async def add_message(
		self,
		content: str = MISSING
	) -> Message | WebhookMessage:
		"""
		Add a message as a response or follow-up. If no message has been sent yet, the message is sent as a response.
		Otherwise, the message will be linked to the response (sent as a follow-up message).
		If the message exceeds the maximum character limit, it will be truncated.
		"""
		return await self.__add_message(content)

	async def __add_message(
		self,
		content: str = MISSING
	) -> Message | WebhookMessage:

		# If a reply has already been sent
		if self.last_message:
			last_message = await self._send_after_last_msg(content)

		# First reply
		else:
			last_message = await self._send_as_first_reply(content)

		self.last_message = last_message
		return last_message

	async def edit_message(
		self,
		content: str = MISSING,
		surname_content: str | None = None,
	) -> Message | WebhookMessage:
		"""
		Send a message as a response. If the response has already been sent, it will be modified.
		If the message exceeds the maximum character limit, it will be truncated.
		"""

		# If a reply has already been sent
		if self.last_message:

			# If the message has a nickname, only the last reply with the same nickname is changed.
			if surname_content:
				last_message_edited = self.last_message_surname.get(surname_content)

				if last_message_edited:
					msg = await last_message_edited.edit(content=self._tuncate_msg_if_overflow(content))
					self.last_message_surname[surname_content] = await last_message_edited.edit(content=self._tuncate_msg_if_overflow(content))
				else:
					msg = await self.__add_message(content)
					self.last_message_surname[surname_content] = msg
			else:
				msg = await self.last_message.edit(content=self._tuncate_msg_if_overflow(content))

		# First reply
		else:
			msg = await self._send_as_first_reply(content)
			if surname_content:
				self.last_message_surname[surname_content] = msg

		return msg

	async def add_code_message(self, content: str, prefix=None, suffix=None):
		"""
		Send a message with markdown code formatting. If the character limit is exceeded, send multiple messages.
		"""
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

		substrings_generator = tools.split_string_by_length(content, max_length)

		first_substring = next(substrings_generator, None)
		if first_substring is None:
			return

		first_substring_formatted = f"```{first_substring}```"
		if not self.ctx.is_expired() and self.ctx.response.is_done():
			self.last_message = await self.ctx.followup.send(first_substring_formatted, wait=True)
		else:
			self.last_message = await self.txt_channel.send(first_substring_formatted)

		last_channel_message = None
		for substring in substrings_generator:
			substring_formatted = f"```{substring}```"

			last_channel_message = await self._get_last_channel_message()

			# If the last message of channel is the last reply
			if last_channel_message.id == self.last_message.id:
				self.last_message = await self.txt_channel.send(content=substring_formatted)
			else:
				self.last_message = await self.ctx.followup.send(
					content=substring_formatted, wait=True
				)

	async def _send_as_first_reply(self, content: str) -> Message | WebhookMessage:
		# If interaction can be used
		if not self.ctx.is_expired() and self.ctx.response.is_done():
			last_message = await self.ctx.followup.send(
				self._tuncate_msg_if_overflow(content), wait=True
			)
		else:
			command_name = self.ctx.command.name if self.ctx.command else "<unknown command>"
			last_message = await self.txt_channel.send(
				self._tuncate_msg_if_overflow(
					f"{self.ctx.user.mention} `/{command_name}` {content}"
				)
			)
		self.last_message = last_message
		return last_message

	async def _send_after_last_msg(self, content: str) -> Message | WebhookMessage:
		if not self.last_message:
			raise Exception("There is no last message")

		last_channel_message = await self._get_last_channel_message()

		# If the last message of channel is the last reply
		if last_channel_message.id == self.last_message.id:
			last_message = await self.txt_channel.send(self._tuncate_msg_if_overflow(content))

		# If not, send a message linked to the last message
		else:
			last_message = await self.last_message.reply(
				self._tuncate_msg_if_overflow(content)
			)
		self.last_message = last_message
		return last_message

	async def _get_last_channel_message(self) -> Message:
		last_channel_message = None
		history = self.txt_channel.history(limit=1)
		async for message in history:
			last_channel_message = message
		if not last_channel_message:
			raise Exception("Channel didn't have history")
		return last_channel_message

	def _tuncate_msg_if_overflow(self, content: str) -> str:
		if content == MISSING or content == "":
			return content
		new_content, is_used = tools.substring_with_end_msg(
			content, MAX_MSG_LENGTH, "{} more characters..."
		)
		if not is_used:
			return content
		return new_content
