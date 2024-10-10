import asyncio
import inspect
from collections import deque
from threading import Event
from typing import Callable, Deque, Optional
import uuid
from pyramid.api.services.discord import IDiscordService
from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.message_queue import IMessageQueueService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.data.message_queue_item import MessageQueueItem

@pyramid_service(interface=IMessageQueueService)
class MessageQueueService(ServiceInjector):

	MIN_PRIORITY = 1
	MAX_PRIORITY = 3

	def __init__(self):
		self.queue: dict[str, MessageQueueItem] = {}
		self.order: dict[int, Deque[str]] = {i: deque() for i in range(self.MIN_PRIORITY, self.MAX_PRIORITY + 1)}
		self.event = Event()
		self.open = True

	def injectService(self,
			logger_service: ILoggerService,
			discord_service: IDiscordService
		):
		self.logger = logger_service
		self.__discord_service = discord_service
		self.logger.info("MessageQueueService had IDiscordService %#x" % (id(self.__discord_service)))

	def add(self, item: MessageQueueItem, unique_id: Optional[str] = None, priority: int = (MIN_PRIORITY + MAX_PRIORITY) // 2) -> str:
		if priority < self.MIN_PRIORITY or priority > self.MAX_PRIORITY:
			raise ValueError("Priority must be between %d and %d." % (self.MIN_PRIORITY, self.MAX_PRIORITY))


		if unique_id is None:
			unique_id = self.generate_unique_id()
		elif unique_id in self.queue:
			self.queue[unique_id] = item
			for p in range(self.MIN_PRIORITY, self.MAX_PRIORITY + 1):
				if unique_id in self.order[p]:
					if p != priority:
						self.order[p].remove(unique_id)
						self.order[priority].append(unique_id)
				return unique_id
				
		self.queue[unique_id] = item
		self.order[priority].append(unique_id)
		self.event.set()
		return unique_id

	async def worker(self) -> None:
		self.logger.info("Message queue started")
		while self.open:
			self.event.wait()
			if not self.open:
				self.logger.info("Message queue closed, stopping worker")
				break
			item_poped = False
			for priority in range(self.MIN_PRIORITY, self.MAX_PRIORITY + 1):
				if not self.order[priority]:
					continue
				unique_id = self.order[priority].popleft()
				item = self.queue.pop(unique_id, None)
				if not item:
					self.logger.info("Message queue has no items, stopping worker")
					break
				item_poped = True

				try:
					result = self.__run_task(item.func, item.loop, **item.kwargs)
					if item.func_success:
						item.func_success(result)
				except Exception as err:
					if item.func_error:
						item.func_error(err)
			if not item_poped and not self.queue:
				self.event.clear()
		self.logger.info("Message queue stopped")

	def __run_task(self, func: Callable, loop: asyncio.AbstractEventLoop, **kwargs):
		# Async func
		if inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func):
			# Async func in loop
			if loop is not None:
				# Async func in loop closed
				if loop.is_closed():
					raise Exception(
						"Unable to call %s.%s cause the loop is closed",
						func.__module__,
						func.__qualname__,
					)
				# Async func in loop open
				result = asyncio.run_coroutine_threadsafe(func(**kwargs), loop).result()
			# Async func classic
			else:
				result = asyncio.run(func(**kwargs))
		# Sync func
		else:
			result = func(**kwargs)
		return result

	def stop(self) -> None:
		if not self.open:
			self.logger.warning("Message queue already stopped")
			return
		self.logger.info("Message queue stopping")
		self.open = False
		self.event.set()

	def generate_unique_id(self) -> str:
		unique_id = None
		while unique_id is None or unique_id in self.queue:
			unique_id = str(uuid.uuid4())
		return unique_id
