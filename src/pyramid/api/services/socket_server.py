from abc import ABC, abstractmethod
from pyramid.data.functional.application_info import ApplicationInfo

class ISocketServerService(ABC):

	@abstractmethod
	def start(self):
		pass
