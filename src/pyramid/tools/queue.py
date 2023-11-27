import asyncio
import inspect
import logging
import traceback
from collections import deque
from concurrent.futures import CancelledError
from threading import Event, Lock, Thread
from typing import Any, Callable, Deque, List


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


def worker(q: Deque[QueueItem], thread_id: int, lock: Lock, event: Event):
	while True:
		if len(q) == 0:
			event.wait()

		if not q:
			event.clear()
			continue

		item: QueueItem = q.pop()

		if item is None:
			break

		try:
			result = run_task(item.func, item.loop, **item.kwargs)

			if item.func_sucess is not None:
				item.func_sucess(result)
		except CancelledError:
			logging.warning(
				"Exception in thread %d :\nTask %s.%s has been cancelled",
				thread_id,
				item.func.__module__,
				item.func.__qualname__,
			)

		except Exception as err:
			if item.func_error is not None:
				item.func_error(err)
			else:
				logging.error(
					"Exception in thread %d :\n%s",
					thread_id,
					"".join(traceback.format_exception(type(err), err, err.__traceback__)),
				)


def run_task(func: Callable, loop: asyncio.AbstractEventLoop | None, **kwargs):
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


class Queue:
	all_queue = deque()

	def __init__(self, threads=1, name=None):
		self.__threads = threads
		self.__queue: Deque[QueueItem | None] = deque()
		self.__event = Event()
		self.__threads_list: List[Thread] = []
		self.__lock = Lock()
		self.__worker = worker

		for thread_id in range(1, self.__threads + 1):
			thread = Thread(
				name=f"{name} n°{thread_id}",
				target=self.__worker,
				args=(self.__queue, thread_id, self.__lock, self.__event),
				daemon=True,
			)
			self.__threads_list.append(thread)

	def register_to_wait_on_exit(self):
		Queue.all_queue.append(self)

	def __del__(self):
		if self in Queue.all_queue:
			Queue.all_queue.remove(self)

	def start(self):
		for thread in self.__threads_list:
			thread.start()

	def add(self, item: QueueItem | None):
		self.__queue.appendleft(item)
		self.__event.set()

	def add_at_start(self, item: QueueItem):
		self.__queue.append(item)
		self.__event.set()

	# Wait for the queue to be empty
	def join(self, timeout: float | None = None):
		for thread in self.__threads_list:
			thread.join(timeout)

	# Add a None item to the queue to signal the thread to exit
	def end(self):
		for _ in range(self.__threads):
			self.add(None)

	def length(self):
		return len(self.__queue)

	@staticmethod
	def wait_for_end(timeout_per_threads: float | None = None):
		for queue in Queue.all_queue:
			queue.end()
		for queue in Queue.all_queue:
			queue.join(timeout_per_threads)
