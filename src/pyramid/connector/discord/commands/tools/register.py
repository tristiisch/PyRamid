import importlib
import inspect
import logging
import pkgutil
from discord.ext.commands import Bot
from pyramid.api.services.tools.register import ServiceRegister
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
	def create_commands(cls, bot: Bot, logger: logging.Logger, command_prefix: str | None = None):
		for type, parameters in cls.__COMMANDS_TO_REGISTER.items():
			class_instance = type(parameters, bot, logger)
			class_instance.register(command_prefix)

	@classmethod
	def inject_tasks(cls):
		for type, parameters in cls.__COMMANDS_TO_REGISTER.items():
			signature = inspect.signature(type.injectService)
			method_parameters = list(signature.parameters.values())

			services_dependencies = []
			for method_parameter in method_parameters:
				dependency_cls = method_parameter.annotation
				dependency_instance = ServiceRegister.get_service(dependency_cls)
				services_dependencies.append(dependency_instance)

			type.injectService(*services_dependencies)
