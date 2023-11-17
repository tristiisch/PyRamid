import logging
from typing import Self

import discord
import tools.utils
from connector.database.history import history_table
from connector.database.sql_methods import SQLMethods
from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, Sequence, String


# @history_table
class User(SQLMethods):
	__tablename__ = "users"

	id = Column(BigInteger, Sequence("user_id_seq"), primary_key=True)
	identifier = Column(String(37), unique=True, nullable=True)
	discord_id = Column(BigInteger, CheckConstraint("discord_id  >= 0"))
	created_at = Column(DateTime(timezone=True))
	is_bot = Column(Boolean)

	def __str__(self):
		return tools.utils.print_human_readable(self)

	@classmethod
	def from_discord_user(cls, user: discord.User) -> Self:
		return cls(
			identifier=f"{user.name}#{user.discriminator}",
			discord_id=user.id,
			created_at=user.created_at,
			is_bot=user.bot,
		)


class UserHandler:
	def __init__(self):
		self.__session = User.create_session()()

	@classmethod
	def save(cls, user: User, self: Self | None = None):
		if not self:
			self = cls()
		self.add_or_update(user)

	def __del__(self):
		self.__session.close()

	def add(self, user: User):
		User.add(user, True, self.__session)
		logging.info("Added '%s'", user)

	def add_or_update(self, user: User):
		user, is_added, is_updated = User.add_or_update(user, True, self.__session)
		if is_added:
			logging.info("Added '%s'", user)
		elif is_updated:
			logging.info("Updated '%s'", user)
		return is_added

	def find(self, name: str) -> User | None:
		user = User.find_unique(self.__session, name=name)

		if user is None:
			logging.info("User '%s' not found", name)
			return
		logging.info("Found '%s'", user)

	def find_all(self) -> User | None:
		users = User.find_all(self.__session)

		if len(users) == 0:
			logging.info("They is no users in table User")
			return
		logging.info("Found :%s", tools.utils.plurial_humain_readable(users))

	def delete(self, name: str) -> bool:
		deleted_lenght = User.delete_by(self.__session, name=name)

		if deleted_lenght == 0:
			logging.info("User '%s' not found for deleting", name)
			return False

		logging.info("%d user%s deleted", deleted_lenght, "s" if deleted_lenght > 1 else "")
		return True
