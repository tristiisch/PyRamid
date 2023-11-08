from typing import Callable
from tools.message_sender import MessageSender

from discord import Interaction
from discord.utils import MISSING
from tools.queue import Queue, QueueItem

MAX_MSG_LENGTH = 2000

queue = Queue(1, "MessageSender")
queue.start()
queue.register_to_wait_on_exit()


class MessageSenderQueued(MessageSender):
	def __init__(self, ctx: Interaction):
		super().__init__(ctx)

	async def waiting(self):
		await super().response_message("Waiting for result ...")

	async def add_message(
		self,
		content: str = MISSING,
		callback: Callable | None = None,
	) -> None:
		queue.add(
			QueueItem(
				"add_message", super().add_message, self.loop, content=content, callback=callback
			)
		)

	async def response_message(
		self,
		content: str = MISSING,
	):
		queue.add(
			QueueItem(
				"response_message", super().response_message, self.loop, content=content
			)
		)

	async def add_code_message(self, content: str, prefix=None, suffix=None):
		queue.add(
			QueueItem(
				"add_code_message", super().add_code_message, self.loop, content=content, prefix=prefix, suffix=suffix
			)
		)

