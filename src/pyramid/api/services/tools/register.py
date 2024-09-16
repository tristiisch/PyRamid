
from collections import defaultdict, deque
import importlib
import inspect
import pkgutil
from typing import Type, TypeVar
from pyramid.api.services.tools.exceptions import ServiceAlreadyNotRegisterException, ServiceAlreadyRegisterException, ServiceCicularDependencyException
from pyramid.api.services.tools.injector import ServiceInjector

T = TypeVar('T')

class ServiceRegister:

	__SERVICE_TO_REGISTER: dict[str, type[ServiceInjector]] = {}
	__SERVICE_REGISTERED: dict[str, ServiceInjector] = {}

	@staticmethod
	def register_service(name: str, type: type[object]):
		if not issubclass(type, ServiceInjector):
			raise TypeError("Service %s is not a subclass of ServiceInjector and cannot be initialized." % name)
		if name in ServiceRegister.__SERVICE_TO_REGISTER:
			already_class_name = ServiceRegister.__SERVICE_TO_REGISTER[name].__name__
			raise ServiceAlreadyRegisterException(
				"Cannot register %s with %s, it is already registered with the class %s."
				% (name, type.__name__, already_class_name)
			)
		ServiceRegister.__SERVICE_TO_REGISTER[name] = type

	@staticmethod
	def import_services():
		package_name = "pyramid.services"
		package = importlib.import_module(package_name)

		for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
			full_module_name = f"{package_name}.{module_name}"
			module = importlib.import_module(full_module_name)

	@staticmethod
	def create_services():
		for name, cls in ServiceRegister.__SERVICE_TO_REGISTER.items():
			class_instance = cls()
			ServiceRegister.__SERVICE_REGISTERED[name] = class_instance

	@staticmethod
	def inject_services():
		# Step 1: Create a graph of dependencies
		dependency_graph = defaultdict(list)
		indegree = defaultdict(int)  # To track the number of dependencies

		# Create instances but delay injecting dependencies
		for name, cls in ServiceRegister.__SERVICE_TO_REGISTER.items():
			class_instance = cls()
			ServiceRegister.__SERVICE_REGISTERED[name] = class_instance

			# Step 2: Parse dependencies for each service
			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())

			for method_parameter in method_parameters:
				dependency_name = method_parameter.annotation.__name__
				if dependency_name not in ServiceRegister.__SERVICE_REGISTERED:
					raise ServiceAlreadyNotRegisterException(
						"Cannot register %s as a dependency for %s because the dependency is not registered."
						% (dependency_name, name)
					)
				# Add an edge in the dependency graph
				dependency_graph[dependency_name].append(name)
				indegree[name] += 1

		# Step 3: Perform a topological sort to determine the order of instantiation
		sorted_services = []
		queue = deque([service for service in ServiceRegister.__SERVICE_TO_REGISTER if indegree[service] == 0])

		while queue:
			service = queue.popleft()
			sorted_services.append(service)

			for dependent in dependency_graph[service]:
				indegree[dependent] -= 1
				if indegree[dependent] == 0:
					queue.append(dependent)

		if len(sorted_services) != len(ServiceRegister.__SERVICE_TO_REGISTER):
			unresolved_services = set(ServiceRegister.__SERVICE_TO_REGISTER) - set(sorted_services)
			raise ServiceCicularDependencyException(
				"Circular dependency detected! The following services are involved in a circular dependency: %s"
				% ', '.join(unresolved_services)
			)

		# Step 4: Inject dependencies in the correct order
		for service_name in sorted_services:
			class_instance = ServiceRegister.__SERVICE_REGISTERED[service_name]
			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())

			services_dependencies = []
			for method_parameter in method_parameters:
				dependency_name = method_parameter.annotation.__name__
				dependency_instance = ServiceRegister.__SERVICE_REGISTERED[dependency_name]
				services_dependencies.append(dependency_instance)

			class_instance.injectService(*services_dependencies)

	@staticmethod
	def get_dependency_tree():
		# Step 1: Build dependency graph
		dependency_graph = defaultdict(list)
		for name, cls in ServiceRegister.__SERVICE_TO_REGISTER.items():
			class_instance = ServiceRegister.__SERVICE_REGISTERED[name]

			signature = inspect.signature(class_instance.injectService)
			method_parameters = list(signature.parameters.values())

			for method_parameter in method_parameters:
				dependency_name = method_parameter.annotation.__name__
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
		all_services = set(ServiceRegister.__SERVICE_TO_REGISTER.keys())
		dependent_services = set(dep for deps in dependency_graph.values() for dep in deps)
		root_services = all_services - dependent_services

		if not root_services:
			raise ServiceCicularDependencyException("No root services found. Possible circular dependencies.")

		# Step 5: Build the tree starting from each root service
		for root in root_services:
			build_tree(root)

		return "Services dependencies :\n" + "\n".join(buffer)


	@staticmethod
	def start_services():
		for name, class_instance in ServiceRegister.__SERVICE_REGISTERED.items():
			class_instance.start()

	@staticmethod
	def get_service(class_type: Type[T]) -> T:
		class_name = class_type.__name__
		return ServiceRegister.__SERVICE_REGISTERED[class_name]