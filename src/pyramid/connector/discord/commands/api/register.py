
import logging
from discord.ext.commands import Bot
from pyramid.connector.discord.commands.api.abc import AbstractCommand
from pyramid.connector.discord.commands.api.parameters import ParametersCommand

COMMANDS_AUTOREGISTRED: dict[type[AbstractCommand], ParametersCommand] = {}

def register_commands(bot: Bot, logger: logging.Logger, command_prefix: str | None = None):
	for cls, parameters in COMMANDS_AUTOREGISTRED.items():
		class_instance = cls(parameters, bot, logger)
		class_instance.register(command_prefix)
		logger.info("%s - %s" % (vars(cls), vars(parameters)))
