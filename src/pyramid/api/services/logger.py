from abc import ABC, abstractmethod
from logging import Logger

class ILoggerService(ABC):
	
	@abstractmethod
	def critical(self, msg, *args, **kwargs):
		pass

	@abstractmethod
	def error(self, msg, *args, **kwargs):
		pass

	@abstractmethod
	def warning(self, msg, *args, **kwargs):
		pass

	@abstractmethod
	def info(self, msg, *args, **kwargs):
		pass

	@abstractmethod
	def debug(self, msg, *args, **kwargs):
		pass

	@abstractmethod
	def log(self, level, msg, *args, **kwargs):
		pass

	@abstractmethod
	def getChild(self, suffix: str) -> Logger:
		pass

	@abstractmethod
	def getLogger(self) -> Logger:
		pass
