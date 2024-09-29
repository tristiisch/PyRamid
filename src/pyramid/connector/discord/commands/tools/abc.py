from abc import ABC, abstractmethod
from discord import Interaction
from discord.ext.commands import Bot

from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

class AbstractCommand(ABC):

	def __init__(self, parameters: ParametersCommand, bot: Bot):
		self.parameters = parameters
		self.bot = bot

	def injectService(self):
		pass

	@abstractmethod
	async def execute(self, ctx: Interaction):
		pass
