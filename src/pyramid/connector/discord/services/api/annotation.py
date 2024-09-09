from pyramid.connector.discord.services.api.register import SERVICE_TO_REGISTER


def pyramid_service():
	def decorator(cls):
		# if not issubclass(cls, AbstractService):
		# 	raise TypeError(f"Class {cls.__name__} must extend from AbstractListener")

		class_name = cls.__name__
		SERVICE_TO_REGISTER[class_name] = cls
		return cls
	return decorator
