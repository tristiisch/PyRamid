
import inspect
import logging
from discord.ext.commands import Bot
from pyramid.connector.discord.commands.api.abc import AbstractCommand
from pyramid.connector.discord.commands.api.parameters import ParametersCommand

COMMANDS_TO_REGISTER: dict[type[AbstractCommand], ParametersCommand] = {}

def register_commands(services: dict[str, object], bot: Bot, logger: logging.Logger, command_prefix: str | None = None):
	for cls, parameters in COMMANDS_TO_REGISTER.items():
		class_instance = cls(parameters, bot, logger)
		class_instance.register(command_prefix)
		# logger.info("%s - %s" % (vars(cls), vars(parameters)))
		# logger.info("services %s" % ", ".join(services.keys()))

		signature = inspect.signature(class_instance.injectService)
		params = list(signature.parameters.values())
		# for param in params:
		# 	logger.info("param %s" % param.annotation)

		# logger.info("params %s" % ", ".join(params))
		dependencies = [services[param.annotation.__name__] for param in params]
		# logger.info("dependencies %s" % (vars(dependencies)))
		class_instance.injectService(*dependencies)
