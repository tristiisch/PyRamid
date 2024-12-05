import asyncio
from typing import Any, Callable


class MessageQueueItem:
	def __init__(
		self,
		func: Callable,
		loop: asyncio.AbstractEventLoop,
		func_success: Callable | None = None,
		func_error: Callable[[Exception], Any] | None = None,
		**kwargs,
	) -> None:
		self.func: Callable = func
		self.loop = loop
		self.func_success = func_success
		self.func_error = func_error
		self.kwargs = kwargs
