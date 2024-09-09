
import logging
from abc import ABC, abstractmethod
from discord.ext.commands import Bot

class ServiceInjector(ABC):

	def __init__(self, bot: Bot, logger: logging.Logger):
		self.bot = bot
		self.logger = logger

	def injectService(self):
		pass
