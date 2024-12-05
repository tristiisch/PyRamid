class ServiceRegisterException(Exception):
	pass

class ServiceAlreadyRegisterException(ServiceRegisterException):
	pass

class ServiceNotRegisteredException(ServiceRegisterException):
	pass

class ServiceCicularDependencyException(ServiceRegisterException):
	pass

class ServiceWasNotOrdedException(ServiceRegisterException):
	pass

