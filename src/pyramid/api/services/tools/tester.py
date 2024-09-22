import inspect
from typing import Optional, Type, TypeVar, cast
from pyramid.api.services.tools.exceptions import ServiceNotRegisterException
from pyramid.api.services.tools.register import ServiceRegister

T = TypeVar('T')

class ServiceStandalone:

	__SERVICE_REGISTERED: dict[str, object] = {}

	@classmethod
	def import_services(cls):
		ServiceRegister.import_services()

	@classmethod
	def set_service(cls, service_interface: Type[T], service_instance: object):
		service_name = service_interface.__name__
		cls.__SERVICE_REGISTERED[service_name] = service_instance

	@classmethod
	def get_service(cls, service_interface: Type[T]) -> T:
		service_name = service_interface.__name__

		if service_name in cls.__SERVICE_REGISTERED:
			return cast(T, cls.__SERVICE_REGISTERED[service_name])

		service_type = ServiceRegister.get_service_registred(service_name)
		class_instance = service_type()

		signature = inspect.signature(class_instance.injectService)
		method_parameters = list(signature.parameters.values())

		services_dependencies = []
		for method_parameter in method_parameters:
			dependency = method_parameter.annotation
			dependency_instance = cls.get_service(dependency)

			services_dependencies.append(dependency_instance)

		class_instance.injectService(*services_dependencies)
		class_instance.start()

		cls.__SERVICE_REGISTERED[service_name] = class_instance

		return cast(T, class_instance)
