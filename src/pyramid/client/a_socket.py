from abc import ABC


class ASocket(ABC):
	def __init__(self) -> None:
		self._from: str
		self._to: str
