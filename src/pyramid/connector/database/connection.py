import logging
import threading
import time
from typing import Any, List

import tools.utils
from sqlalchemy import Column, Engine, Inspector, Table, create_engine, inspect, text
from sqlalchemy.engine.interfaces import ReflectedColumn
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy_utils import create_database, database_exists
from tools.configuration.configuration import Configuration


class DatabaseConnection:
	ENGINE: Engine | None = None
	BASES: list[DeclarativeMeta] = []

	def __init__(self, config: Configuration):
		database_url = "%s://%s:%s@%s%s/%s" % (
			config.database__type,
			config.database__username,
			config.database__password,
			config.database__host,
			f":{config.database__port}" if config.database__port > 0 else "",
			config.database__name,
		)
		self._logger = logging.getLogger("database")

		self.__engine = create_engine(database_url, echo=False)
		DatabaseConnection.ENGINE = self.__engine

	def connect(self):
		self.ping_database(5, False)

		if not database_exists(self.__engine.url):
			create_database(self.__engine.url)

		if len(DatabaseConnection.BASES) != 0:
			for base in DatabaseConnection.BASES:
				DatabaseConnection.create_table(base)

			DatabaseConnection.BASES.clear()

		ping_thread = threading.Thread(target=self.ping_database, daemon=True)
		ping_thread.start()

	def ping_database(self, interval: int = 30, infinite: bool = True):
		Session = sessionmaker(bind=self.__engine)
		last_error_message = None

		while True:
			with Session() as session:
				error = self.check_connection(session)
				if not error:
					if last_error_message is not None:
						self._logger.info("Database is now available !")
					last_error_message = None
					if not infinite:
						if last_error_message is None:
							self._logger.info("Database is available")
						break
					time.sleep(interval)
					continue
				error_message = str(error)
				if error_message != last_error_message:
					last_error_message = error_message
					self._logger.warning("Database is unavailable:\n%s", error)
				time.sleep(interval)

	def check_connection(self, session: Session) -> None | DBAPIError:
		try:
			session.execute(text("SELECT 1"))
			session.commit()
			return None
		except DBAPIError as err:
			return err

	@staticmethod
	def create_table(base: DeclarativeMeta):
		engine = DatabaseConnection.ENGINE
		if engine is None:
			return
		inspector: Inspector = inspect(engine)

		# Get tables registered
		mappers: frozenset[Mapper] = base._sa_registry.mappers
		for mapper in mappers:
			cls = mapper.base_mapper.class_
			local_table: Table = cls.__table__
			local_table_name: str = local_table.name
			if not isinstance(local_table_name, str):
				continue

			# Check if the table exists in the database
			local_columns: List[Column[Any]] = DatabaseConnection._get_local_columns(
				mapper, local_table_name
			)
			if not inspector.has_table(local_table_name):
				logging.info(
					"Table '%s' does not exist in the database. Skipping checking columns...",
					local_table_name,
				)
				continue

			# Check and create columns if they don't exist
			remote_columns: List[ReflectedColumn] = DatabaseConnection._get_remote_columns(
				inspector, local_table_name
			)
			for column in local_columns:
				existing_column = next(
					(col for col in remote_columns if col["name"] == column.name),
					None,
				)
				if existing_column is not None:
					continue

				DatabaseConnection.add_column(local_table_name, column)
				# Check if table is created
				new_remote_columns = DatabaseConnection._get_remote_columns(
					inspect(engine), local_table_name
				)
				is_added = False
				for remote_column in new_remote_columns:
					if column.key == remote_column["name"]:
						is_added = True
						break

				if is_added is True:
					logging.info("Column '%s' added successfully", column.key)
				else:
					logging.info("Failed to add column '%s'", column.key)

		base.metadata.create_all(engine)

	@staticmethod
	def _get_local_columns(mapper: Mapper, table_name: str):
		local_columns: List[Column[Any]] = mapper.columns.values()
		if not isinstance(local_columns, List):
			raise Exception("local_columns is not a list")

		data = [
			[
				local_column.name,
				local_column.type,
				local_column.primary_key,
				local_column.unique if isinstance(local_column.unique, bool) else False,
				local_column.nullable,
				True if local_column.server_default else None,
				local_column.autoincrement,
				local_column.comment,
				local_column.computed,
				local_column.identity,
				local_column.dialect_options if local_column.dialect_options else None,
			]
			for local_column in local_columns
		]
		hsa = tools.utils.human_string_array(
			data,
			[
				"name",
				"type",
				"primary",
				"unique",
				"nullable",
				"default",
				"autoincrement",
				"comment",
				"computed",
				"identity",
				"dialect_options",
			],
		)
		logging.debug("Columns of table defined in code '%s'\n%s\n", table_name, hsa)

		return local_columns

	@staticmethod
	def _get_remote_columns(inspector: Inspector, table_name: str):
		remote_columns: List[ReflectedColumn] = inspector.get_columns(table_name)
		primary_columns = inspector.get_pk_constraint(table_name)["constrained_columns"]
		uniques_columns = inspector.get_unique_constraints(table_name)
		data = [
			[
				remote_column["name"],
				remote_column["type"],
				True if remote_column["name"] in primary_columns else False,
				True
				if any(remote_column["name"] in item["column_names"] for item in uniques_columns)
				else False,
				remote_column["nullable"],
				remote_column["default"],
				remote_column.get("autoincrement", None),
				remote_column.get("comment", None),
				remote_column.get("computed", None),
				remote_column.get("identity", None),
				remote_column.get("dialect_options", None),
			]
			for remote_column in remote_columns
		]
		hsa = tools.utils.human_string_array(
			data,
			[
				"name",
				"type",
				"primary",
				"unique",
				"nullable",
				"default",
				"autoincrement",
				"comment",
				"computed",
				"identity",
				"dialect_options",
			],
		)
		logging.debug("Columns of table in remote database '%s'\n%s\n", table_name, hsa)

		return remote_columns

	@staticmethod
	def add_column(table_name: str, column: Column):
		engine = DatabaseConnection.ENGINE
		if engine is None:
			return
		with engine.connect() as connection:
			column_name = column.key
			column_type = column.type
			column_nullable = "NULL" if column.nullable else "NOT NULL"
			column_default = f"DEFAULT {column.default}" if column.default is not None else ""
			column_primary_key = "PRIMARY KEY" if column.primary_key else ""
			column_unique = "UNIQUE" if column.unique else ""

			sql_statement = "ALTER TABLE %s ADD COLUMN %s %s %s %s %s %s" % (
				table_name,
				column_name,
				column_type,
				column_nullable,
				column_default,
				column_primary_key,
				column_unique,
			)
			sql_statement = " ".join(sql_statement.split()) + ";"
			logging.info("SQL Execute '%s'", sql_statement)
			connection.execute(text(sql_statement))
			connection.commit()

	@staticmethod
	def register_class(base: DeclarativeMeta):
		if DatabaseConnection.ENGINE is None:
			DatabaseConnection.BASES.append(base)
		else:
			DatabaseConnection.create_table(base)
