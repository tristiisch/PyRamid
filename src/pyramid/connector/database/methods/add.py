from typing import Self, overload

from connector.database.methods.base import SQLMethodsBase
from sqlalchemy.orm import Session


class SQLMethodsAdd(SQLMethodsBase):
	__abstract__ = True

	@classmethod
	@overload
	def add(cls, obj: Self, refresh: bool):
		...

	@classmethod
	@overload
	def add(cls, obj: Self, refresh: bool, session: Session):
		...

	@classmethod
	def add(cls, obj: Self, refresh: bool, session: Session | None = None):
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				cls._add_internal(session, obj, refresh)
		else:
			cls._add_internal(session, obj, refresh)

	@classmethod
	@overload
	def add_if_not_exists(cls, obj: Self, refresh: bool):
		...

	@classmethod
	@overload
	def add_if_not_exists(cls, obj: Self, refresh: bool, session: Session):
		...

	@classmethod
	def add_if_not_exists(cls, obj: Self, refresh: bool, session: Session | None = None):
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				cls._add_internal(session, obj, refresh, True)
		else:
			cls._add_internal(session, obj, refresh, True)

	@classmethod
	def _add_internal(cls, session: Session, obj: Self, refresh = False, ignore_if_exists = False):
		duplicates = cls._check_duplicate(session, obj, not ignore_if_exists)
		if duplicates:
			return
		session.add(obj)
		session.commit()
		if refresh is True:
			session.refresh(obj)
