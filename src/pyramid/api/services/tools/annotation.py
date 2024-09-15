from typing import Optional
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.api.services.tools.register import ServiceRegister


def pyramid_service(*, interface: Optional[type] = None):
	def decorator(cls):
		class_name = cls.__name__
		if not issubclass(cls, ServiceInjector):
			raise TypeError("Class %s must inherit from ServiceInjector" % class_name)
		
		service_name = class_name
		if interface is not None:
			service_name = interface.__name__

		ServiceRegister.register_service(service_name, cls)
		return cls
	return decorator
