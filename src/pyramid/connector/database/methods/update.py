from datetime import datetime
import json
from typing import Any, Callable, Self, overload

from connector.database.methods.base import SQLMethodsBase
from sqlalchemy.orm import Session


class SQLMethodsUpdate(SQLMethodsBase):
	__abstract__ = True

	@classmethod
	@overload
	def update(cls, update_obj: Self) -> Self:
		...

	@classmethod
	@overload
	def update(cls, update_obj: Self, session: Session) -> Self:
		...

	@classmethod
	def update(cls, update_obj: Self, session: Session | None = None) -> Self:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				existing_obj = cls._get_similar(session, update_obj)
				return existing_obj
		else:
			existing_obj = cls._get_similar(session, update_obj)
			cls._update_internal(session, existing_obj, update_obj)
			return existing_obj

	@classmethod
	@overload
	def update_fast(cls, **kwargs) -> Self:
		...

	@classmethod
	@overload
	def update_fast(cls, session: Session, **kwargs) -> Self:
		...

	@classmethod
	def update_fast(cls, session: Session | None = None, **kwargs) -> Self:
		if session is None:
			Session = cls.create_session()
			with Session() as session:
				existing_obj = cls._get_similar(session, **kwargs)
				cls._update_internal(session, existing_obj, **kwargs)
				return existing_obj
		else:
			existing_obj = cls._get_similar(session, **kwargs)
			cls._update_internal(session, existing_obj, **kwargs)
			return existing_obj

	# ------------------------------------------------------

	# @classmethod
	# @overload
	# def __update_internal(cls, session: Session, obj: Self) -> Self:
	# 	...

	# @classmethod
	# @overload
	# def __update_internal(cls, session: Session, **kwargs) -> Self:
	# 	...

	# @classmethod
	# def __update_internal(cls, session, obj: Self | None=None, **kwargs):
	# 	if obj is not None:
	# 		return cls.__update_internal_2(session, obj)
	# 	elif kwargs:
	# 		return cls.__update_internal_2(session, **kwargs)
	# 	else:
	# 		raise ValueError("Invalid arguments")

	@classmethod
	def _get_similar(
		cls, session: Session, obj: Self | None = None, raise_err: bool = True, **kwargs
	) -> Self | None:
		key, value = cls._get_attribute_unique_defined(obj, **kwargs)
		existing_obj = session.query(cls).filter(getattr(cls, key) == value).first()
		if raise_err is True and existing_obj is None:
			raise ValueError(f"Object to update does not exist in the database with {key}={value}")
		return existing_obj
	
	@classmethod
	def _serialize(cls, obj) -> str | None:
		if not obj:
			return None
		if isinstance(obj, str):
			return obj
		elif isinstance(obj, datetime):
			return obj.isoformat()
		
		# return str(obj)
		return json.dumps(obj, default=str)

	@classmethod
	def _deserialize(cls, obj) -> str | None:
		if not obj:
			return None
		elif isinstance(obj, str):
			return obj
		return json.loads(obj)

	@classmethod
	def _update_internal(
		cls,
		session: Session,
		existing_obj: Self,
		update_obj: Self | None = None,
		refresh: bool = False,
		**kwargs,
	):
		changed_attributes = cls.__get_changed_attributes(existing_obj, update_obj, **kwargs)
		if not changed_attributes:
			return False

		# history_data: dict[str, Any] = {}
		# for key, value in changed_attributes.items():
		# 	history_data[f"old_{key}"] = cls._serialize(getattr(existing_obj, key, None))
		# 	setattr(existing_obj, key, value)
		# 	history_data[f"new_{key}"] = cls._serialize(value)

		# session.commit()

		if hasattr(existing_obj, "History"):
			user_history = existing_obj.History(original_id=existing_obj.id, data=changed_attributes)
			session.add(user_history)
		session.commit()
		
		if refresh is True:
			session.refresh(existing_obj)
		return True

	@classmethod
	@overload
	def __get_changed_attributes(cls, existing_obj: Self, update_obj: Self) -> dict[str, Any]:
		...

	@classmethod
	@overload
	def __get_changed_attributes(cls, existing_obj: Self, **kwargs) -> dict[str, Any]:
		...

	@classmethod
	def __get_changed_attributes(cls, existing_obj: Self, update_obj: Self | None = None, **kwargs) -> dict[str, Any]:
		if update_obj is not None:
			return cls.__get_changed_attributes_internal(
				existing_obj, lambda key: getattr(update_obj, key)
			)
		elif kwargs:
			return cls.__get_changed_attributes_internal(existing_obj, kwargs.get)
		else:
			raise ValueError("Invalid arguments")

	@classmethod
	def __get_changed_attributes_internal(cls, existing_obj: Self, getter: Callable[[str], Any]) -> dict[str, Any]:
		changed_attributes = {}
		for column in cls.__table__.columns:
			key = column.key
			# new_value = cls._serialize(getter(key))
			new_value = getter(key)
			if new_value is None:
				continue
			# old_value = cls._serialize(getattr(existing_obj, key, None))
			old_value = getattr(existing_obj, key, None)

			if old_value != new_value:
				# changed_attributes[key] = new_value
				changed_attributes[f"old_{key}"] = old_value
				setattr(existing_obj, key, new_value)
				changed_attributes[f"new_{key}"] = new_value
		return changed_attributes
