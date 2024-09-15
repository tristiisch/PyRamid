from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.tools import utils
from pyramid.tools.configuration.configuration_load import ConfigurationFromEnv, ConfigurationFromYAML
from pyramid.tools.configuration.configuration_save import ConfigurationToYAML

@pyramid_service(interface=IConfigurationService)
class ConfigurationService(IConfigurationService, ConfigurationFromYAML, ConfigurationToYAML, ConfigurationFromEnv, ServiceInjector):

	def injectService(self,
			logger_service: ILoggerService
		):
		self.logger = logger_service
		super().set_logger(logger_service)

	def start(self):
		self.load()

	def load(self, config_file: str = "config.yml", use_env_vars: bool = True) -> bool:
		"""
		Loads configuration values from environment variables and/or a configuration file.

		Parameters:
		- use_env_vars (bool): If True, loads configuration values from environment variables.

		Returns:
		- bool: True if the loading process is successful, False otherwise.
		"""
		keys_length = utils.count_public_variables(self)

		# Load from environment variables if enabled
		result_1 = True
		if use_env_vars:
			raw_values_env = self._get_env_vars()
			result_values = self._transform_all(raw_values_env, keys_length)
			result_1 = self._validate_all(
				raw_values_env, result_values, "env vars", True, keys_length
			)

		# Load raw values from environment variables and config file
		try:
			raw_values_file = self._get_file_vars(config_file)
			result_values = self._transform_all(raw_values_file, keys_length)
			result_2 = self._validate_all(
				raw_values_file, result_values, "file", keys_length=keys_length
			)
		except FileNotFoundError as err:
			if not result_1:
				self.logger.critical(
					"Unable to read configuration file '%s' :\n%s", config_file, err
				)
				return False
			result_2 = True

		return result_1 and result_2

	def save(self, file_name):
		"""
		Saves the configuration values to a YAML file.

		Parameters:
		- file_name (str): The name of the file to which the configuration will be saved.
		"""
		self._save_to_yaml(file_name)
