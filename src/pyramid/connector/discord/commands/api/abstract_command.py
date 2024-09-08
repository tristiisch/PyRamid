from abc import ABC, abstractmethod
import copy
import logging
from typing import Optional
from discord import Interaction
from discord.app_commands import Command
from discord.ext.commands import Bot
from discord.utils import MISSING

from pyramid.connector.discord.commands.api.parameters_command import ParametersCommand

class AbstractCommand(ABC):

	def __init__(self, parameters: ParametersCommand, bot: Bot, logger: logging.Logger):
		self.bot = bot
		self.logger = logger
		self.parameters = parameters

	@abstractmethod
	async def execute(self, ctx: Interaction):
		pass

	def register(self, command_prefix: Optional[str] = None):
		if command_prefix is not None:
			self.parameters.name = "%s_%s" % (command_prefix, self.parameters.name)

		command = Command(
			name=self.parameters.name,
			description=self.parameters.description,
			callback=self.execute,
			nsfw=self.parameters.nsfw,
			parent=None,
			auto_locale_strings=self.parameters.auto_locale_strings,
			extras=self.parameters.extras,
		)
		# self.bot.tree.add_command(command, guilds=self.parameters.guilds)
		self.bot.tree.add_command(command)
