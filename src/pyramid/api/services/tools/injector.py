from abc import ABC, abstractmethod
from discord.ext.commands import Bot

class ServiceInjector(ABC):

	def injectService(self):
		pass

	def start(self):
		pass

	def stop(self):
		pass
