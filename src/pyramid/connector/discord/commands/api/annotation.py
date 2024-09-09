import re
from textwrap import TextWrapper
from discord.utils import MISSING

from pyramid.connector.discord.commands.api.abc import AbstractCommand
from pyramid.connector.discord.commands.api.parameters import ParametersCommand
from pyramid.connector.discord.commands.api.register import COMMANDS_AUTOREGISTRED


def discord_command(*, parameters: ParametersCommand):
	def decorator(cls):
		if not issubclass(cls, AbstractCommand):
			raise TypeError(f"Class {cls.__name__} must extend from AbstractCommand")

		if parameters.name is MISSING:
			class_name = cls.__name__
			if class_name.endswith("Command"):
				class_name = class_name[:-len("Command")]
			parameters.name = _camel_to_snake(class_name)
		
		if parameters.description is MISSING:
			if cls.__doc__ is None:
				parameters.description = '…'
			else:
				parameters.description = _shorten(cls.__doc__)
		COMMANDS_AUTOREGISTRED[cls] = parameters
		return cls
	return decorator


def _camel_to_snake(name: str):
	snake_case = ""
	for i, char in enumerate(name):
		if char.isupper() and i != 0:
			snake_case += "_" + char.lower()
		else:
			snake_case += char.lower()
	return snake_case

def _shorten(
	input: str,
	*,
	_wrapper: TextWrapper = TextWrapper(width=100, max_lines=1, replace_whitespace=True, placeholder='…')
) -> str:
	"""
	Copy of func :func:`discord.utils._shorten`.
	"""

	try:
		# split on the first double newline since arguments may appear after that
		input, _ = re.split(r'\n\s*\n', input, maxsplit=1)
	except ValueError:
		pass
	return _wrapper.fill(' '.join(input.strip().split()))
