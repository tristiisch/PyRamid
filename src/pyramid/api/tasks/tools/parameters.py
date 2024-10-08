import asyncio
from threading import Thread

from pyramid.api.tasks.tools.injector import TaskInjector


class ParametersTask:
	
	def __init__(self, stop_own_loop = False):
		self.loop: asyncio.AbstractEventLoop
		self.thread: Thread
		self.cls_instance: TaskInjector
		self.stop_own_loop = stop_own_loop
