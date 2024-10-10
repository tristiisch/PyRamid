import asyncio
from typing import Any, Callable


class QueueItem:
	def __init__(
		self,
		name,
		func: Callable,
		loop: asyncio.AbstractEventLoop | None = None,
		func_sucess: Callable | None = None,
		func_error: Callable[[Exception], Any] | None = None,
		**kwargs,
	) -> None:
		self.name = name
		self.func: Callable = func
		self.loop = loop
		self.func_sucess = func_sucess
		self.func_error = func_error
		self.kwargs = kwargs
