from typing import Any, Callable

from data.functional.messages.message_sender import MessageSender
from discord import Interaction, Message, WebhookMessage
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

	def add_message(
		self,
		content: str = MISSING,
		callback: Callable[[Message | WebhookMessage], Any] | None = None,
	) -> None:
		queue.add(
			QueueItem("add_message", super().add_message, self.loop, callback, content=content)
		)

	def edit_message(
		self,
		content: str = MISSING,
		surname_content: str | None = None,
		callback: Callable[[Message | WebhookMessage], Any] | None = None,
	):
		queue.add(
			QueueItem(
				"response_message",
				super().edit_message,
				self.loop,
				callback,
				content=content,
				surname_content=surname_content,
			)
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
