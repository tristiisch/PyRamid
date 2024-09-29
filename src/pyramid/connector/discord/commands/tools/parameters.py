from typing import Any, Dict, Optional, Sequence, Union

from discord.abc import Snowflake
from discord.app_commands import locale_str
from discord.utils import MISSING

class ParametersCommand:
	def __init__(self,
		name: str = MISSING,
		description: str | locale_str = MISSING,
		nsfw: bool = False,
		guild: Optional[Snowflake] = MISSING,
		guilds: Sequence[Snowflake] = MISSING,
		auto_locale_strings: bool = True,
		extras: Dict[Any, Any] = MISSING,
		only_guild = False
	):
		self.name = name
		self.description = description
		self.nsfw = nsfw
		self.guild = guild
		self.guilds = guilds
		self.auto_locale_strings = auto_locale_strings
		self.extras = extras
		self.only_guild = only_guild
