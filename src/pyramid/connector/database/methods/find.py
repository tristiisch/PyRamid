from typing import List, Self, overload

from connector.database.methods.base import SQLMethodsBase
from sqlalchemy.orm import Session


class SQLMethodsFind(SQLMethodsBase):
	__abstract__ = True

	@classmethod
	@overload
	def find_all(cls) -> List[Self]:
		...

	@classmethod
	@overload
	def find_all(cls, session: Session) -> List[Self]:
		...

	@classmethod
	def find_all(cls, session: Session | None = None) -> List[Self]:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				return cls._find_all_internal(session)
		else:
			return cls._find_all_internal(session)

	@classmethod
	def _find_all_internal(cls, session: Session) -> List[Self]:
		query = session.query(cls)
		result = query.all()
		return result

	@classmethod
	@overload
	def find(cls, **kwargs) -> List[Self]:
		...

	@classmethod
	@overload
	def find(cls, session: Session, **kwargs) -> List[Self]:
		...

	@classmethod
	def find(cls, session: Session | None = None, **kwargs) -> List[Self]:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				return cls._find_internal(session, **kwargs)
		else:
			return cls._find_internal(session, **kwargs)

	@classmethod
	def _find_internal(cls, session: Session, **kwargs) -> List[Self]:
		cls._is_column_exists(**kwargs)

		query = session.query(cls)
		for key, value in kwargs.items():
			query = query.filter(getattr(cls, key) == value)
		result = query.all()
		return result

	@classmethod
	@overload
	def find_unique(cls, **kwargs) -> Self:
		...

	@classmethod
	@overload
	def find_unique(cls, session: Session, **kwargs) -> Self:
		...

	@classmethod
	def find_unique(cls, session: Session | None = None, **kwargs) -> Self:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				return cls._find_unique_internal(session, **kwargs)
		else:
			return cls._find_unique_internal(session, **kwargs)

	@classmethod
	def _find_unique_internal(cls, session: Session, **kwargs) -> Self:
		if len(kwargs) != 1:
			raise ValueError("Exactly one key-value pair is required")

		cls._is_column_exists(**kwargs)
		key, value = next(iter(kwargs.items()))
		cls._is_column_unique(key)

		query = session.query(cls).filter_by(**{key: value})
		result = query.first()
		return result
