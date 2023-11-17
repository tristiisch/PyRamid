from typing import Self, overload

from connector.database.methods.base import SQLMethodsBase
from sqlalchemy.orm import Session


class SQLMethodsDelete(SQLMethodsBase):
	__abstract__ = True

	@classmethod
	@overload
	def delete(cls, obj: Self):
		...

	@classmethod
	@overload
	def delete(cls, obj: Self, session: Session):
		...

	@classmethod
	def delete(cls, obj: Self, session: Session | None = None):
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				cls._delete_internal(session, obj)
		else:
			cls._delete_internal(session, obj)


	@classmethod
	def _delete_internal(cls, session: Session, obj: Self):
		session.delete(obj)
		session.commit()

	@classmethod
	@overload
	def delete_by(cls, **kwargs):
		...

	@classmethod
	@overload
	def delete_by(cls, session: Session, **kwargs):
		...

	@classmethod
	def delete_by(cls, session: Session | None = None, **kwargs) -> int:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				return cls._delete_by_internal(session, **kwargs)
		else:
			return cls._delete_by_internal(session, **kwargs)

	@classmethod
	def _delete_by_internal(cls, session: Session, **kwargs) -> int:
		cls._is_column_exists(**kwargs)
		query = session.query(cls)
		for key, value in kwargs.items():
			query = query.filter(getattr(cls, key) == value)
		deleted_lenght = query.delete()
		return deleted_lenght
