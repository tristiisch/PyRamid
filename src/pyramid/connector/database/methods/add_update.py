from typing import Self, overload

from connector.database.methods.add import SQLMethodsAdd
from connector.database.methods.update import SQLMethodsUpdate
from sqlalchemy.orm import Session


class SQLMethodsAddUpdate(SQLMethodsAdd, SQLMethodsUpdate):
	__abstract__ = True

	@classmethod
	@overload
	def add_or_update(cls, obj: Self, refresh: bool) -> tuple[Self, bool, bool]:
		...

	@classmethod
	@overload
	def add_or_update(cls, obj: Self, refresh: bool, session: Session) -> tuple[Self, bool, bool]:
		...

	@classmethod
	def add_or_update(cls, obj: Self, refresh: bool, session: Session | None = None) -> tuple[Self, bool, bool]:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				return cls._add_or_update_internal(session, obj, refresh)
		else:
			return cls._add_or_update_internal(session, obj, refresh)

	@classmethod
	def _add_or_update_internal(cls, session: Session, obj: Self, refresh: bool = False) -> tuple[Self, bool, bool]:
		Session = cls.create_session()
		with Session() as session:
			existing_obj = cls._get_similar(session, obj, False)
			if existing_obj is None:
				cls._add_internal(session, obj, refresh)
				return obj, True, False
			cls._update_internal(session, existing_obj, obj, refresh)
			updated = cls._update_internal(session, existing_obj, obj, refresh)
			return existing_obj, False, updated
