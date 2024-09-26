
import asyncio
import importlib
import inspect
import logging
import pkgutil
import signal
from threading import Thread
from typing import TypeVar
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask

T = TypeVar('T')

class TaskRegister:

	__TASKS_REGISTERED: dict[str, ParametersTask] = {}

	@classmethod
	def import_tasks(cls):
		package_name = "pyramid.tasks"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			importlib.import_module(full_module_name)

	@classmethod
	def register_tasks(cls, type: type[object], parameters: ParametersTask):
		if not issubclass(type, TaskInjector):
			raise TypeError("Service %s is not a subclass of TaskInjector and cannot be initialized." % type.__name__)
		parameters.task_cls = type()
		cls.__TASKS_REGISTERED[type.__name__] = parameters

	@classmethod
	def inject_tasks(cls):
		for name, parameters in cls.__TASKS_REGISTERED.items():
			signature = inspect.signature(parameters.task_cls.injectService)
			method_parameters = list(signature.parameters.values())

			services_dependencies = []
			for method_parameter in method_parameters:
				dependency_cls = method_parameter.annotation
				dependency_instance = ServiceRegister.get_service(dependency_cls)
				services_dependencies.append(dependency_instance)

			parameters.task_cls.injectService(*services_dependencies)

	@classmethod
	def __handle_signal(cls, signum: int, frame):
		logging.info("Received signal %d. shutting down ..." % signum)

		for name, parameters in cls.__TASKS_REGISTERED.items():
			async def shutdown(loop: asyncio.AbstractEventLoop):
				await parameters.task_cls.stop_asyc()
				parameters.loop.stop()
			asyncio.run_coroutine_threadsafe(shutdown(parameters.loop), parameters.loop)

	@classmethod
	def start_tasks(cls):
		previous_handler = signal.signal(signal.SIGTERM, cls.__handle_signal)
		for name, parameters in cls.__TASKS_REGISTERED.items():

			parameters.loop = asyncio.new_event_loop()

			def running(loop: asyncio.AbstractEventLoop):
				asyncio.set_event_loop(loop)

				loop.create_task(parameters.task_cls.worker_asyc())
				try:
					loop.run_forever()
				finally:
					loop.close()

			parameters.thread = Thread(name=name, target=running, args=(parameters.loop,))

		for name, parameters in cls.__TASKS_REGISTERED.items():
			parameters.thread.start()

		for name, parameters in cls.__TASKS_REGISTERED.items():
			parameters.thread.join()

		signal.signal(signal.SIGTERM, previous_handler)
		logging.info("All tasks are stopped")
