from abc import ABC, abstractmethod
from typing import Any, Literal

from deezer import Resource


class ADeezerClient(ABC):
	@abstractmethod
	async def async_request(
		self,
		method: str,
		path: str,
		parent: Resource | None = None,
		resource_type: type[Resource] | None = None,
		resource_id: int | None = None,
		paginate_list=False,
		**params,
	) -> Any | list[Any] | dict[str, Any] | Resource | Literal[True]:
		...
