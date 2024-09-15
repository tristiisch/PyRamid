class ServiceRegisterException(Exception):
	pass

class ServiceAlreadyRegisterException(ServiceRegisterException):
	pass

class ServiceAlreadyNotRegisterException(ServiceRegisterException):
	pass

class ServiceCicularDependencyException(ServiceRegisterException):
	pass
