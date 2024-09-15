import logging
from abc import ABC, abstractmethod
from typing import Optional
from discord import Interaction
from discord.app_commands import Command
from discord.ext.commands import Bot

from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

class AbstractCommand(ABC):

	def __init__(self, parameters: ParametersCommand, bot: Bot, logger: logging.Logger):
		self.parameters = parameters
		self.bot = bot
		self.logger = logger

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
		# TODO check this usage
		# self.bot.tree.add_command(command, guilds=self.parameters.guilds)
		self.bot.tree.add_command(command)

	def injectService(self):
		pass

	@abstractmethod
	async def execute(self, ctx: Interaction):
		pass
