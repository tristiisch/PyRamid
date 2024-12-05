from typing import Optional
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask
from pyramid.api.tasks.tools.register import TaskRegister


def pyramid_task(*, parameters: ParametersTask):
	def decorator(cls):
		class_name = cls.__name__
		if not issubclass(cls, TaskInjector):
			raise TypeError("Class %s must inherit from TaskInjector" % class_name)
		
		TaskRegister.register_tasks(cls, parameters)
		return cls
	return decorator
