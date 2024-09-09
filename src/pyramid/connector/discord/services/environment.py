
from pyramid.connector.discord.services.api.annotation import pyramid_service
from pyramid.data.environment import Environment


@pyramid_service()
class EnvironmentService:

	def __init__(self):
		self.__type: Environment = Environment.PRODUCTION

	def get_type(self):
		return self.__type

	def get_type_name(self):
		return self.__type.name.capitalize()
	
	def set_type(self, environnement: Environment):
		self.__type = environnement
