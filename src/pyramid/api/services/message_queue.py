from abc import ABC, abstractmethod
from typing import Optional

from pyramid.data.message_queue_item import MessageQueueItem

class IMessageQueueService(ABC):

	@abstractmethod
	async def worker(self) -> None:
		pass

	@abstractmethod
	def stop(self) -> None:
		pass

	@abstractmethod
	def add(self, item: MessageQueueItem, unique_id: Optional[str] = None, priority: int = 5) -> str:
		pass

	@abstractmethod
	def add_first(self, item: MessageQueueItem, unique_id: Optional[str] = None) -> str:
		pass
