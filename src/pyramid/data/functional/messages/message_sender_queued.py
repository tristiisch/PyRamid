from typing import Any, Callable

from pyramid.data.functional.messages.message_sender import MessageSender
from discord import Interaction, Message, WebhookMessage
from discord.utils import MISSING
from pyramid.data.queue_item import QueueItem
from pyramid.tools.main_queue import MainQueue

MAX_MSG_LENGTH = 2000

class MessageSenderQueued(MessageSender):
	def __init__(self, ctx: Interaction):
		self.ctx = ctx
		super().__init__(ctx)

	def add_message(
		self,
		content: str = MISSING,
		callback: Callable[[Message | WebhookMessage], Any] | None = None,
	) -> None:
		MainQueue.instance.add(
			QueueItem("add_message", super().add_message, self.loop, callback, content=content)
		)

	def edit_message(
		self,
		content: str = MISSING,
		surname_content: str | None = None,
		callback: Callable[[Message | WebhookMessage], Any] | None = None,
	):
		MainQueue.instance.add(
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
		MainQueue.instance.add(
			QueueItem(
				"add_code_message",
				super().add_code_message,
				self.loop,
				content=content,
				prefix=prefix,
				suffix=suffix,
			)
		)
