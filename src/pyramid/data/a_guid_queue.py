from abc import ABC, abstractmethod
from typing import Optional

from data.track import Track

class AGuildQueue(ABC):
	@abstractmethod
	def is_playing(self) -> bool:
		pass

	@abstractmethod
	def stop(self) -> bool:
		pass

	@abstractmethod
	async def exit(self) -> bool:
		pass

	@abstractmethod
	def pause(self) -> bool:
		pass

	@abstractmethod
	def resume(self) -> bool:
		pass

	@abstractmethod
	def has_next(self) -> bool:
		pass

	@abstractmethod
	def next(self) -> bool:
		pass

	@abstractmethod
	def shuffle(self) -> bool:
		pass

	@abstractmethod
	def remove(self, index: int) -> Optional[Track]:
		pass

	@abstractmethod
	def goto(self, index: int) -> int:
		pass

	@abstractmethod
	def queue_list(self) -> Optional[str]:
		pass