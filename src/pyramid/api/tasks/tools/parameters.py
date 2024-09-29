import asyncio
from threading import Thread

from pyramid.api.tasks.tools.injector import TaskInjector


class ParametersTask:
	
	def __init__(self):
		self.loop: asyncio.AbstractEventLoop
		self.thread: Thread
		self.cls_instance: TaskInjector
