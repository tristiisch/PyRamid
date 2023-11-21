from typing import Self

import discord
import tools.utils
from connector.database.sql_methods import SQLMethods
from sqlalchemy import BigInteger, CheckConstraint, Column, Sequence, String

class Guild(SQLMethods):
	__tablename__ = "guilds"

	id = Column(BigInteger, Sequence(f"{__name__.lower()}_id_seq"), primary_key=True)
	discord_id = Column(BigInteger, CheckConstraint("discord_id >= 0"), unique=True)
	identifier = Column(String)
	local = Column(String)

	def __str__(self):
		return tools.utils.print_human_readable(self)

	@classmethod
	def from_discord_guild(cls, guild: discord.Guild) -> Self:
		return cls(
			identifier=guild.name,
			discord_id=guild.id,
			local=guild.preferred_locale.name
		)
