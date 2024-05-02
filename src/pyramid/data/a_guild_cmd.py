from abc import ABC, abstractmethod

from discord import Interaction

from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued


class AGuildCmd(ABC):
	@abstractmethod
	async def stop(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		pass

	@abstractmethod
	async def pause(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		pass

	@abstractmethod
	async def resume(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		pass

	@abstractmethod
	async def resume_or_pause(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		pass

	@abstractmethod
	async def next(self, ms: MessageSenderQueued, ctx: Interaction) -> bool:
		pass

	@abstractmethod
	async def shuffle(self, ms: MessageSenderQueued, ctx: Interaction):
		pass

	@abstractmethod
	async def remove(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		pass

	@abstractmethod
	async def goto(self, ms: MessageSenderQueued, ctx: Interaction, number_in_queue: int):
		pass
