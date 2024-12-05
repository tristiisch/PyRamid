import inspect
from typing import Type, TypeVar, cast, get_type_hints
from pyramid.api.services.tools.register import ServiceRegister

T = TypeVar('T')

class ServiceStandalone:

	SERVICE_REGISTERED: dict[str, object] = {}

	@classmethod
	def import_services(cls):
		ServiceRegister.import_services()

	@classmethod
	def set_service(cls, service_interface: Type[T], service_instance: object):
		service_name = service_interface.__name__
		cls.SERVICE_REGISTERED[service_name] = service_instance

	@classmethod
	def get_service(cls, service_interface: Type[T]) -> T:
		service_name = service_interface.__name__

		if service_name in cls.SERVICE_REGISTERED:
			return cast(T, cls.SERVICE_REGISTERED[service_name])

		service_type = ServiceRegister.get_service_registred(service_name)
		class_instance = service_type()

		signature = inspect.signature(class_instance.injectService)
		method_parameters = list(signature.parameters.values())
		type_hints = get_type_hints(class_instance.injectService)

		services_dependencies = []
		for method_parameter in method_parameters:
			dependency = type_hints[method_parameter.name]
			dependency_instance = cls.get_service(dependency)

			services_dependencies.append(dependency_instance)

		class_instance.injectService(*services_dependencies)
		class_instance.start()

		cls.SERVICE_REGISTERED[service_name] = class_instance

		return cast(T, class_instance)
