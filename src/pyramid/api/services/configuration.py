from abc import ABC, abstractmethod
from pyramid.data.environment import Environment

class IConfigurationService(ABC):

	def __init__(self):
		self.discord__token: str = ""
		self.discord__ffmpeg: str = ""
		self.deezer__arl: str = ""
		self.deezer__folder: str = ""
		self.spotify__client_id: str = ""
		self.spotify__client_secret: str = ""
		self.general__limit_tracks: int = 0
		self.mode: Environment = Environment.PRODUCTION
		self.version: str = ""

	@abstractmethod
	def load(self, config_file: str = "config.yml", use_env_vars: bool = True) -> bool:
		"""
		Loads configuration values from environment variables and/or a configuration file.

		Parameters:
		- use_env_vars (bool): If True, loads configuration values from environment variables.

		Returns:
		- bool: True if the loading process is successful, False otherwise.
		"""
		pass

	@abstractmethod
	def save(self, file_name: str):
		"""
		Saves the configuration values to a YAML file.

		Parameters:
		- file_name (str): The name of the file to which the configuration will be saved.
		"""
		pass
