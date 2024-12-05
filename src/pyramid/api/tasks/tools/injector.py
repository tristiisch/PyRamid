from abc import ABC, abstractmethod
from discord.ext.commands import Bot

class TaskInjector(ABC):

	def injectService(self):
		pass

	async def worker_asyc(self):
		pass

	async def stop_asyc(self):
		pass
