import logging
from typing import Callable

import tools.utils as tools
from data.functional.messages.message_sender import MessageSender
from discord import Interaction
from discord.utils import MISSING
from tools.queue import Queue, QueueItem

MAX_MSG_LENGTH = 2000

queue = Queue(1, "MessageSender")
queue.start()
queue.register_to_wait_on_exit()


class MessageSenderQueued(MessageSender):
	def __init__(self, ctx: Interaction):
		self.ctx = ctx
		super().__init__(ctx)

	async def waiting(self):
		await super().response_message("Waiting for result ...")

	def add_message(
		self,
		content: str = MISSING,
		callback: Callable | None = None,
	) -> None:
		queue.add(
			QueueItem(
				"add_message", super().add_message, self.loop, content=content, callback=callback
			)
		)

	def response_message(
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
			queue.add(
				QueueItem(
					"Edit last response",
					self.last_reponse.edit,
					self.loop,
					content=content,
				)
			)

		elif self.ctx.response.is_done():
			def on_error(err):
				if err.code == 50027:  # 401 Unauthorized : Invalid Webhook Token
					logging.warning(
						"Unable to modify original response, send message instead", exc_info=True
					)
					self.add_message(content, lambda msg: setattr(self, "last_response", msg))
				else:
					raise err

			queue.add(
				QueueItem(
					"Edit response",
					self.ctx.edit_original_response,
					self.loop,
					None,
					on_error,
					content=content,
				)
			)
		else:
			queue.add(
				QueueItem(
					"Send followup as response",
					self.ctx.response.send_message,
					self.loop,
					content=content,
				)
			)

		queue.add(
			QueueItem("response_message", super().response_message, self.loop, content=content)
		)

	def add_code_message(self, content: str, prefix=None, suffix=None):
		queue.add(
			QueueItem(
				"add_code_message",
				super().add_code_message,
				self.loop,
				content=content,
				prefix=prefix,
				suffix=suffix,
			)
		)
