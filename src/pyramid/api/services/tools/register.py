
from collections import defaultdict, deque
import importlib
import inspect
import pkgutil
from typing import Any, Type, TypeVar, get_type_hints
from pyramid.api.services.tools.exceptions import ServiceNotRegisteredException, ServiceAlreadyRegisterException, ServiceCicularDependencyException, ServiceWasNotOrdedException
from pyramid.api.services.tools.injector import ServiceInjector

T = TypeVar('T')

class ServiceRegister:

	SERVICES_REGISTRED: dict[str, type[ServiceInjector]] = {}
	SERVICES_INSTANCES: dict[str, ServiceInjector] = {}
	ORDERED_SERVICES: list[str] | None = None

	@classmethod
	def import_services(cls):
		package_name = "pyramid.services"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			importlib.import_module(full_module_name)

	@classmethod
	def register_service(cls, interface_name: str, type: type[object]):
		type_name = type.__name__
		if not issubclass(type, ServiceInjector):
			raise TypeError("Service %s is not a subclass of ServiceInjector and cannot be initialized." % type_name)
		if interface_name in cls.SERVICES_REGISTRED:
			already_class_name = cls.SERVICES_REGISTRED[interface_name].__module__ + ' ' + cls.SERVICES_REGISTRED[interface_name].__name__
			raise ServiceAlreadyRegisterException(
				"Cannot register service %s with %s, it is already registered with the class %s."
				% (interface_name, type_name, already_class_name)
			)
		cls.SERVICES_REGISTRED[interface_name] = type

	@classmethod
	def enable(cls):
		cls.create_services()
		cls.determine_service_order()
		cls.inject_services()
		cls.start_services()

	@classmethod
	def determine_service_order(cls):
		"""This method is not recommended.

		Please call the `enable` method instead, which takes care of performing
		the actions in the correct order.
		"""
		# Step 1: Create a graph of dependencies
		dependency_graph = defaultdict(list)
		indegree = defaultdict(int)  # To track the number of dependencies

		# Parse dependencies but delay injecting
		for name, service_type in cls.SERVICES_REGISTRED.items():
			class_instance = cls.SERVICES_INSTANCES[name]

			# Step 2: Parse dependencies for each service
			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())
			type_hints = get_type_hints(class_instance.injectService)

			for method_parameter in method_parameters:
				dependency_name = type_hints[method_parameter.name].__name__
				if dependency_name not in cls.SERVICES_INSTANCES:
					raise ServiceNotRegisteredException(
						f"Cannot register {dependency_name} as a dependency for {name} because the dependency is not registered."
					)
				# Add an edge in the dependency graph
				dependency_graph[dependency_name].append(name)
				indegree[name] += 1

		# Step 3: Perform a topological sort to determine the order of instantiation
		sorted_services = []
		queue = deque([service for service in cls.SERVICES_REGISTRED if indegree[service] == 0])

		while queue:
			service = queue.popleft()
			sorted_services.append(service)

			for dependent in dependency_graph[service]:
				indegree[dependent] -= 1
				if indegree[dependent] == 0:
					queue.append(dependent)

		if len(sorted_services) != len(cls.SERVICES_REGISTRED):
			unresolved_services = set(cls.SERVICES_REGISTRED) - set(sorted_services)
			raise ServiceCicularDependencyException(
				f"Circular dependency detected! The following services are involved in a circular dependency: {', '.join(unresolved_services)}"
			)

		cls.ORDERED_SERVICES = sorted_services

	@classmethod
	def inject_services(cls):
		"""This method is not recommended.

		Please call the `enable` method instead, which takes care of performing
		the actions in the correct order.
		"""
		if not cls.ORDERED_SERVICES:
			raise ServiceWasNotOrdedException("Failed to determine service startup order.")

		# Inject dependencies in the correct order
		for service_name in cls.ORDERED_SERVICES:
			class_instance = cls.SERVICES_INSTANCES[service_name]
			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())
			type_hints = get_type_hints(class_instance.injectService)

			services_dependencies = []
			for method_parameter in method_parameters:
				dependency_name = type_hints[method_parameter.name].__name__
				dependency_instance = cls.SERVICES_INSTANCES[dependency_name]
				services_dependencies.append(dependency_instance)

			class_instance.injectService(*services_dependencies)

	@classmethod
	def create_services(cls):
		"""This method is not recommended.

		Please call the `enable` method instead, which takes care of performing
		the actions in the correct order.
		"""
		for name, service_type in cls.SERVICES_REGISTRED.items():
			class_instance = service_type()
			cls.SERVICES_INSTANCES[name] = class_instance

	@classmethod
	def start_services(cls):
		"""This method is not recommended.

		Please call the `enable` method instead, which takes care of performing
		the actions in the correct order.
		"""
		if not cls.ORDERED_SERVICES:
			raise ServiceWasNotOrdedException("Failed to determine service startup order.")

		for service_name in cls.ORDERED_SERVICES:
			class_instance = cls.SERVICES_INSTANCES[service_name]
			class_instance.start()

	@classmethod
	def get_dependency_tree(cls):
		# Step 1: Build dependency graph
		dependency_graph = defaultdict(list)
		for name, class_instance in cls.SERVICES_INSTANCES.items():

			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())
			type_hints = get_type_hints(class_instance.injectService)

			for method_parameter in method_parameters:
				dependency_name = type_hints[method_parameter.name].__name__
				dependency_graph[dependency_name].append(name)

		# Step 2: Internal buffer for storing the tree structure
		buffer = []

		def append_to_buffer(line):
			buffer.append(line)

		# Step 3: Recursive function to build the tree structure
		def build_tree(node, prefix="", last=True):
			""" Recursively builds the tree structure and stores it in the buffer. """
			connector = "└── " if last else "├── "
			append_to_buffer(prefix + connector + node)

			prefix += "    " if last else "│   "
			children = dependency_graph[node]
			for i, child in enumerate(children):
				build_tree(child, prefix, i == len(children) - 1)

		# Step 4: Find root services (those with no dependencies)
		all_services = set(cls.SERVICES_REGISTRED.keys())
		dependent_services = set(dep for deps in dependency_graph.values() for dep in deps)
		root_services = all_services - dependent_services

		if not root_services:
			raise ServiceCicularDependencyException("No root services found. Possible circular dependencies.")

		# Step 5: Build the tree starting from each root service
		for root in root_services:
			build_tree(root)

		return "Services tree :\n" + "\n".join(buffer)

	@classmethod
	def get_service_registred(cls, class_name: str) -> type[ServiceInjector]:
		if class_name not in cls.SERVICES_REGISTRED:
			raise ServiceNotRegisteredException(
				"Cannot get %s because the service is not registered." % (class_name)
			)
		return cls.SERVICES_REGISTRED[class_name]

	@classmethod
	def get_service(cls, class_type: Type[T]) -> T:
		class_name = class_type.__name__
		if class_name not in cls.SERVICES_INSTANCES:
			raise ServiceNotRegisteredException(
				"Cannot get %s because the service is not started." % (class_name)
			)
		return cls.SERVICES_INSTANCES[class_name] # type: ignore
