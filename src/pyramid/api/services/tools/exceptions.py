class ServiceRegisterException(Exception):
	pass

class ServiceAlreadyRegisterException(ServiceRegisterException):
	pass

class ServiceNotRegisterException(ServiceRegisterException):
	pass

class ServiceCicularDependencyException(ServiceRegisterException):
	pass
