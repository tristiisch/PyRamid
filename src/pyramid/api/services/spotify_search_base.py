


from abc import ABC, abstractmethod
from typing import Any

class ISpotifySearchBaseService(ABC):

	@abstractmethod
	async def items(
		self,
		results: dict[str, Any],
		item_name="items"
	) -> list[dict[str, Any]] | None:
		pass

	@abstractmethod
	async def items_max(
		self,
		results: dict[str, Any],
		limit: int | None = None,
		item_name="items"
	) -> list[Any] | None:
		pass
