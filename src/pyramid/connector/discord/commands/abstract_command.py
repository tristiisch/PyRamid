from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional, Union

from discord import Interaction
from discord.app_commands import Group, Command, locale_str
from discord.ext.commands import Bot
from discord.utils import MISSING

import pyramid.tools.utils as tools

class AbstractCommand(ABC):

	def __init__(self, bot: Bot, logger: logging.Logger):
		self.bot = bot
		self.logger = logger

	def name(self) -> Union[str, locale_str]:
		class_name = self.__class__.__name__

		if class_name.endswith("Command"):
			command_name = class_name[:-len("Command")]
		else:
			command_name = class_name
		command_name = tools.camel_to_snake(command_name)
		return command_name

	def description(self) -> Union[str, locale_str]:
		return ""

	def nsfw(self) -> bool:
		return False

	def parent(self) -> Optional[Group]:
		return None

	def auto_locale_strings(self) -> bool:
		return True

	def extras(self) -> Dict[Any, Any]:
		return MISSING

	@abstractmethod
	async def execute(self, ctx: Interaction):
		pass

	def register(self, command_prefix: Optional[str] = None):
		if command_prefix is not None:
			command_name = "%s_%s" % (command_prefix, self.name())
		else:
			command_name = self.name()
		command = Command(
			name=command_name,
			description=self.description(),
			callback=self.execute,
			nsfw=self.nsfw(),
			parent=self.parent(),
			auto_locale_strings=self.auto_locale_strings(),
			extras=self.extras(),
		)
		self.bot.tree.add_command(command, guild=MISSING, guilds=MISSING, override=False)
