from abc import ABC, abstractmethod
from typing import Any


class AEngineTools(ABC):
	@abstractmethod
	def extract_from_url(self, url) -> tuple[int | str, Any | None] | tuple[None, None]:
		pass
