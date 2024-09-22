from typing import Optional
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.api.services.tools.register import ServiceRegister


def pyramid_service(*, interface: Optional[type] = None):
	def decorator(cls):
		class_name: str = cls.__name__		
		service_name = class_name
		if interface is not None:
			service_name = interface.__name__

		ServiceRegister.register_service(service_name, cls)
		return cls
	return decorator
