from sqlalchemy import Column, Integer, Sequence, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from connector.database.methods.base import SQLMethodsBase

Base = SQLMethodsBase

class HistoryMixin:
	id = Column(Integer, Sequence("history_id_seq"), primary_key=True)
	updated_at = Column(DateTime(timezone=True), server_default=func.now())
	data = Column(JSON)

def __create_history_table(cls: Base):
	class_name = f"{cls.__name__}History"
	history_table = type(
		class_name,
		(Base, HistoryMixin),
		{
			"__tablename__": f"{cls.__tablename__}_history",
			"original_id": Column(Integer, ForeignKey(f"{cls.__tablename__}.{cls._get_column_primary()}"), nullable=False)
		}
	)
	return history_table

def history_table(cls):
    cls.History = __create_history_table(cls)
    return cls
