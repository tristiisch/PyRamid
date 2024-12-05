
from pyramid.api.services import IInformationService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.data.functional.application_info import ApplicationInfo

@pyramid_service(interface=IInformationService)
class InformationService(IInformationService, ServiceInjector):

	def __init__(self):
		self._info = ApplicationInfo()

	def get(self) -> ApplicationInfo:
		return self._info
