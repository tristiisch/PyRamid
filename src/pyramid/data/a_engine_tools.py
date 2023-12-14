import abc
from abc import ABC
from typing import Any


class AEngineTools(ABC):
	@abc.abstractmethod
	def extract_from_url(self, url) -> tuple[int | str, Any | None] | tuple[None, None]:
		pass
