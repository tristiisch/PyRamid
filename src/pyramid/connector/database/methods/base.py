from typing import Self, overload

import tools.utils
from _collections_abc import dict_keys
from connector.database.connection import DatabaseConnection
from sqlalchemy import or_
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()
DatabaseConnection.register_class(Base)


class SQLMethodsBase(Base):
	__abstract__ = True
	BaseOriginal = Base

	@classmethod
	def create_session(cls):
		Session = sessionmaker(bind=DatabaseConnection.ENGINE)
		return Session

	@classmethod
	def _is_column_exists(cls, **kwargs):
		unknown_columns = [key for key, _ in kwargs.items() if key not in cls.__table__.columns]
		if len(unknown_columns) != 0:
			raise ValueError(
				"Columns '%s' does not exist in %s" % ", ".join(unknown_columns), cls.__name__
			)

	@classmethod
	def _is_column_unique(cls, column):
		primary_column = cls._get_column_primary()
		unique_columns = cls._get_columns_uniques()
		unique_columns.append(primary_column)

		if not unique_columns:
			raise ValueError(f"No unique columns found in {cls.__name__}")

		if column not in unique_columns:
			raise ValueError(f"{column} is not a unique column in {cls.__name__}")

	@classmethod
	def _is_column_primary(cls, column):
		primary_column = cls._get_column_primary()

		if column != primary_column:
			raise ValueError(f"{column} is not a unique column in {cls.__name__}")

	@classmethod
	def _check_duplicate(cls, session: Session, obj: Self):
		result = cls._get_duplicate(session, obj)

		lenght_result = len(result)
		if lenght_result == 0:
			return

		plural_form = "s" if lenght_result != 1 else ""
		msg_error = "Similar object%s of '%s' already exists :%s" % (
			plural_form,
			obj,
			tools.utils.plurial_humain_readable(result),
		)
		raise ValueError(msg_error)

	@classmethod
	def _get_duplicate_primary(cls, session: Session, obj: Self) -> Self | None:
		"""
		Get object by primary key
		"""
		primary_column = cls._get_column_primary()
		query = session.query(cls).filter(getattr(cls, primary_column) == getattr(obj, primary_column))
		result = query.first()
		return result

	@classmethod
	def _get_duplicate(cls, session: Session, obj: Self) -> list[Self]:
		"""
		Get objects by same key on unique column 
		"""
		unique_columns = cls._get_columns_uniques()
		query = session.query(cls).filter(
			or_(*[getattr(cls, column) == getattr(obj, column) for column in unique_columns])
		)
		result = query.all()
		return result

	@classmethod
	def _get_column_primary(cls) -> str:
		for table_column in cls.__table__.columns:
			if table_column.primary_key:
				return table_column.key
		raise ValueError("No primary columns found %s", cls.__name__)

	@classmethod
	def _get_columns_uniques(cls) -> list[str]:
		unique_columns = [
			table_column.key for table_column in cls.__table__.columns if table_column.unique
		]
		return unique_columns

	@classmethod
	@overload
	def _get_attribute_unique_defined(cls, obj: Self):
		...

	@classmethod
	@overload
	def _get_attribute_unique_defined(cls, **kwargs):
		...
	

	@classmethod
	def _get_attribute_unique_defined(cls, obj=None, **kwargs):
		"""
		Get the first unique column key and its corresponding value from the provided object or keyword arguments.

		Parameters:
		- obj (Optional[Self]): An instance of the class.
		OR
		- kwargs (Optional[Dict[str, Any]]): Keyword arguments representing attribute values.

		Returns:
		Tuple[str, Any]: A tuple containing the unique column key and its corresponding value.
		"""
		if obj is not None:
			keys = obj.__dict__
		elif kwargs:
			# keys = list(kwargs.keys())
			keys = kwargs.keys()
		else:
			raise ValueError("Invalid arguments")

		key = cls.__get_column_unique_defined(keys)
		if obj is not None:
			value = getattr(obj, key)
		else:
			value = kwargs[key]
		return key, value

	@classmethod
	def __get_column_unique_defined(cls, keys: dict | dict_keys):
		# Try to find the primary key column defined in the object
		primary_columns = cls._get_column_primary()
		for column in primary_columns:
			if column in keys:
				return column

		# If not found, use the first unique column as the primary key
		primary_columns = cls._get_columns_uniques()
		for column in primary_columns:
			if column in keys:
				return column

		raise ValueError(f"No unique column key found in {cls}")
