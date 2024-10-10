from abc import ABC, abstractmethod
from pyramid.data.functional.application_info import ApplicationInfo

class IInformationService(ABC):

	@abstractmethod
	def get(self) -> ApplicationInfo:
		pass
