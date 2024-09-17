import importlib
import inspect
import logging
import pkgutil
from discord.ext.commands import Bot
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

class CommandRegister:

	__COMMANDS_TO_REGISTER: dict[type[AbstractCommand], ParametersCommand] = {}

	@classmethod
	def register_command(cls, type: type[AbstractCommand], parameterCommand: ParametersCommand):
		CommandRegister.__COMMANDS_TO_REGISTER[type] = parameterCommand

	@classmethod
	def import_commands(cls):
		package_name = "pyramid.connector.discord.commands"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			importlib.import_module(full_module_name)

	@classmethod
	def create_commands(cls, services: dict[str, object], bot: Bot, logger: logging.Logger, command_prefix: str | None = None):
		for cls, parameters in cls.__COMMANDS_TO_REGISTER.items():
			class_instance = cls(parameters, bot, logger)
			class_instance.register(command_prefix)
			signature = inspect.signature(class_instance.injectService)
			parameters = list(signature.parameters.values())
			dependencies = [services[param.annotation.__name__] for param in parameters]
			class_instance.injectService(*dependencies)
