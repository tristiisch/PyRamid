import importlib
import inspect
import logging
import pkgutil
from discord.ext.commands import Bot
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

class CommandRegister:

	__COMMANDS_TO_REGISTER: dict[type[AbstractCommand], ParametersCommand] = {}

	@staticmethod
	def register_command(type: type[AbstractCommand], parameterCommand: ParametersCommand):
		CommandRegister.__COMMANDS_TO_REGISTER[type] = parameterCommand

	@staticmethod
	def import_commands():
		package_name = "pyramid.connector.discord.commands"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			module = importlib.import_module(full_module_name)

	@staticmethod
	def create_commands(services: dict[str, object], bot: Bot, logger: logging.Logger, command_prefix: str | None = None):
		for cls, parameters in CommandRegister.__COMMANDS_TO_REGISTER.items():
			class_instance = cls(parameters, bot, logger)
			class_instance.register(command_prefix)
			signature = inspect.signature(class_instance.injectService)
			parameters = list(signature.parameters.values())
			dependencies = [services[param.annotation.__name__] for param in parameters]
			class_instance.injectService(*dependencies)
