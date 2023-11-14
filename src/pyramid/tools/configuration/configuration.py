import logging
from logging import Logger

from data.environment import Environment
from tools.configuration.configuration_save import ConfigurationToYAML
from tools.configuration.configuration_load import ConfigurationFromEnv, ConfigurationFromYAML


class Configuration(ConfigurationFromYAML, ConfigurationToYAML, ConfigurationFromEnv):
	def __init__(self, logger: Logger | None = None):
		"""
		Initializes a Configuration object with default values and an optional logger.

		Parameters:
		- logger (Logger): Optional logger for logging messages. If not provided, a default logger named "config" is used.
		"""
		self.discord__token: str = ""
		self.discord__ffmpeg: str = ""
		self.deezer__arl: str = ""
		self.deezer__folder: str = ""
		self.spotify__client_id: str = ""
		self.spotify__client_secret: str = ""
		self.general__limit_tracks: int = 0
		self.mode: Environment = Environment.PRODUCTION
		self.version: str = ""

		if logger is None:
			self.__logger = logging.getLogger("config")
		else:
			self.__logger = logger
		super().__init__(self.__logger)

	def load(self, config_file: str = "config.yml", use_env_vars: bool = True) -> bool:
		"""
		Loads configuration values from environment variables and/or a configuration file.

		Parameters:
		- use_env_vars (bool): If True, loads configuration values from environment variables.

		Returns:
		- bool: True if the loading process is successful, False otherwise.
		"""
		keys_length = 9

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
				self.__logger.critical(
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
