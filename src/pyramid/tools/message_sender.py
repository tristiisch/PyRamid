import asyncio
import logging
from typing import Callable

import tools.utils as tools
from discord import Interaction, Message, TextChannel, WebhookMessage
from discord.errors import HTTPException
from discord.utils import MISSING
from tools.queue import Queue, QueueItem

MAX_MSG_LENGTH = 2000

queue = Queue(1, "MessageSender")
queue.start()
queue.register_to_wait_on_exit()


class MessageSender:
	def __init__(self, ctx: Interaction):
		self.__ctx = ctx
		if ctx.channel is None:
			raise NotImplementedError("Unable to create a MessageSender without channel")
		if not isinstance(ctx.channel, TextChannel):
			raise NotImplementedError("Unable to create a MessageSender without text channel")
		self.txt_channel: TextChannel = ctx.channel
		self.last_reponse: Message | WebhookMessage | None = None
		self.loop: asyncio.AbstractEventLoop = ctx.client.loop

	"""
	Add a message as a response or follow-up. If no message has been sent yet, the message is sent as a response.
	Otherwise, the message will be linked to the response (sent as a follow-up message).
	If the message exceeds the maximum character limit, it will be truncated.
	"""

	async def add_message(
		# def add_message(
		self,
		content: str = MISSING,
		callback: Callable | None = None,
	) -> None:
		if content != MISSING and content != "":
			new_content, is_used = tools.substring_with_end_msg(
				content, MAX_MSG_LENGTH, "{} more characters..."
			)
			if is_used:
				content = new_content

		if not self.__ctx.response.is_done():
			# msg = await self.txt_channel.send(content)
			queue.add(
				QueueItem(
					"Send reponse", self.txt_channel.send, self.loop, callback, content=content
				)
			)
		else:
			# msg = await self.__ctx.followup.send(
			# 	content,
			# 	wait=True,
			# )
			queue.add(
				QueueItem(
					"Send followup",
					self.__ctx.followup.send,
					self.loop,
					callback,
					content=content,
					wait=True,
				)
			)
		# return msg

	"""
	Send a message as a response. If the response has already been sent, it will be modified.
	If it is not possible to modify it, a new message will be sent as a follow-up.
	If the message exceeds the maximum character limit, it will be truncated.
	"""

	async def response_message(
		# def response_message(
		self,
		content: str = MISSING,
	):
		if content != MISSING and content != "":
			new_content, is_used = tools.substring_with_end_msg(
				content, MAX_MSG_LENGTH, "{} more characters..."
			)
			if is_used:
				content = new_content

		if self.last_reponse is not None:
			self.last_reponse.edit(content=content)

		elif self.__ctx.response.is_done():
			try:
				# await self.__ctx.edit_original_response(
				# 	content=content,
				# )
				queue.add(
					QueueItem(
						"Edit response",
						self.__ctx.edit_original_response,
						self.loop,
						content=content,
					)
				)
			except HTTPException as err:
				if err.code == 50027:  # 401 Unauthorized : Invalid Webhook Token
					logging.warning(
						"Unable to modify original response, send message instead", exc_info=True
					)
					# self.last_reponse = await self.add_message(content)
					await self.add_message(content, lambda msg: setattr(self, "last_response", msg))
				else:
					raise err
		else:
			# await self.__ctx.response.send_message(
			# 	content=content,
			# )
			queue.add(
				QueueItem(
					"Send followup as response",
					self.__ctx.response.send_message,
					self.loop,
					content=content,
				)
			)

	"""
	Send a message with markdown code formatting. If the character limit is exceeded, send multiple messages.
	"""

	async def add_code_message(self, content: str, prefix=None, suffix=None):
		# def add_code_message(self, content: str, prefix=None, suffix=None):
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

		if not self.__ctx.response.is_done():
			first_substring = next(substrings_generator, None)
			if first_substring is not None:
				first_substring_formatted = f"```{first_substring}```"
				# await self.__ctx.response.send_message(content=first_substring_formatted)
				queue.add(
					QueueItem(
						"Send code as response",
						self.__ctx.response.send_message,
						self.loop,
						content=first_substring_formatted,
					)
				)

		for substring in substrings_generator:
			substring_formatted = f"```{substring}```"
			# await self.__ctx.followup.send(content=substring_formatted)
			queue.add(
				QueueItem(
					"Send code as followup",
					self.__ctx.followup.send,
					self.loop,
					content=substring_formatted,
				)
			)
