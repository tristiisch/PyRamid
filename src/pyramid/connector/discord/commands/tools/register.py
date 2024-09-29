import importlib
import inspect
import logging
import pkgutil
from typing import Optional
from discord.ext.commands import Bot
from discord.app_commands import Command
from discord.app_commands.installs import AppCommandContext
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.exception import CommandAlreadyRegisterException, CommandNameAlreadyRegisterException
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

class CommandRegister:

	__COMMANDS_REGISTERED: dict[type[AbstractCommand], ParametersCommand] = {}
	__COMMANDS_INSTANCE: dict[str, AbstractCommand] = {}

	@classmethod
	def register_command(cls, type: type[AbstractCommand], parameters: ParametersCommand):
		if type in cls.__COMMANDS_REGISTERED:
			raise CommandAlreadyRegisterException(
				"Cannot register command %s it is already registered." % (type.__name__)
			)
		cls.__COMMANDS_REGISTERED[type] = parameters

	@classmethod
	def import_commands(cls):
		package_name = "pyramid.connector.discord.commands"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			importlib.import_module(full_module_name)

	@classmethod
	def create_commands(cls, bot: Bot, command_prefix: str | None = None):
		for type, parameters in cls.__COMMANDS_REGISTERED.items():
			cls_instance = type(parameters, bot)
			if command_prefix is not None:
				cls_instance.parameters.name = "%s_%s" % (command_prefix, cls_instance.parameters.name)
			if cls_instance.parameters.name in cls.__COMMANDS_INSTANCE:
				cls_already_instance = cls.__COMMANDS_INSTANCE[cls_instance.parameters.name]
				raise CommandNameAlreadyRegisterException(
					"Cannot register command %s with %s, it is already registered with the class %s."
					% ( cls_instance.parameters.name, type.__name__, cls_already_instance.__class__.__name__)
				)

			allowed_contexts: Optional[AppCommandContext] = None
			if cls_instance.parameters.only_guild is True:
				allowed_contexts = AppCommandContext(guild=True)

			discord_command = Command(
				name=cls_instance.parameters.name,
				description=cls_instance.parameters.description,
				callback=cls_instance.execute,
				nsfw=cls_instance.parameters.nsfw,
				parent=None,
				auto_locale_strings=cls_instance.parameters.auto_locale_strings,
				extras=cls_instance.parameters.extras,
				allowed_contexts=allowed_contexts
			)
			# TODO check this usage
			# self.bot.tree.add_command(command, guilds=command.parameters.guilds)
			cls_instance.bot.tree.add_command(discord_command)
			cls.__COMMANDS_INSTANCE[cls_instance.parameters.name] = cls_instance

	@classmethod
	def inject_commands(cls):
		for type, cls_instance in cls.__COMMANDS_INSTANCE.items():
			signature = inspect.signature(cls_instance.injectService)
			method_parameters = list(signature.parameters.values())

			services_dependencies = []
			for method_parameter in method_parameters:
				dependency_cls = method_parameter.annotation
				dependency_instance = ServiceRegister.get_service(dependency_cls)
				services_dependencies.append(dependency_instance)

			cls_instance.injectService(*services_dependencies)
