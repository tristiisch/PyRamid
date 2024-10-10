import os
import re
from abc import ABC
from typing import Any, Callable, List, Optional

import yaml
from pyramid.data.environment import Environment
from pyramid.api.services.logger import ILoggerService


class ConfigurationFromEnv(ABC):

	def _get_env_vars(self) -> dict[str, str]:
		# Load values from environment variables
		env_sys_var = self.__get_sys_env_vars()

		env_secret_var = self.__read_files_in_directory("/run/secrets")
		env_sys_var.update(env_secret_var)

		return env_sys_var

	def __get_sys_env_vars(self) -> dict[str, str]:
		# Load values from environment variables
		return {str(key).lower(): str(value) for key, value in os.environ.items()}

	def __read_files_in_directory(self, directory) -> dict[str, str]:
		env_vars = {}
		if os.path.isdir(directory):
			files = os.listdir(directory)
			for file_name in files:
				file_path = os.path.join(directory, file_name)
				if os.path.isfile(file_path):
					file_vars = self.__load_env_vars_from_file(file_path)
					env_vars.update(file_vars)
		return env_vars

	def __load_env_vars_from_file(self, file) -> dict[str, str]:
		env_vars = {}
		with open(file, "r") as f:
			for line in f:
				# Ignore lines starting with '#' and whitespace characters
				line = line.strip()
				if not line or line.startswith("#"):
					continue

				# Split key-value pairs
				key, value = line.split("=", 1)
				env_vars[key.strip().lower()] = value.strip()

		return env_vars


class ConfigurationFromYAML(ABC):

	def set_logger(self, logger: ILoggerService):
		self.logger = logger

	def _get_file_vars(self, file_name: str) -> dict[str, str]:
		# Load from YAML file
		with open(file_name, "r") as config_file:
			config_data: dict = yaml.safe_load(config_file)
			raw_values: dict[str, str] = {}

			for key, value in config_data.items():
				self.__find_file_values(raw_values, value, key)
			return raw_values

	def __find_file_values(self, raw_values: dict[str, str], config_values: dict | str, key: str):
		if isinstance(config_values, dict):
			for child_key, child_value in config_values.items():
				self.__find_file_values(raw_values, child_value, f"{key}__{child_key}")
			return
		raw_values[key.lower()] = config_values

	def _transform_all(self, v: dict[str, str], keys_length=0):
		r: List[tuple[str, None | Any, str | bool]] = [] * keys_length

		# Validate and set values
		r.append(self.__check(v, "discord.token", r"^[a-zA-Z0-9\.\-_]+"))
		r.append(self.__check(v, "discord.ffmpeg", is_path=True))
		r.append(self.__check(v, "deezer.arl", r"^[a-fA-F0-9]{192}$"))
		r.append(self.__check(v, "deezer.folder", is_path=True))
		r.append(self.__check(v, "spotify.client_id", r"^[a-zA-Z0-9]{32}$"))
		r.append(self.__check(v, "spotify.client_secret", r"^[a-zA-Z0-9]{32}$"))
		r.append(self.__check(v, "general.limit_tracks", is_int=True))
		r.append(self.__check(v, "version"))

		def mode_validation(input: str):
			input = input.replace("-", "_").upper()
			if input not in Environment.__members__:
				return "The value should be one of %s" % ", ".join(Environment.__members__)
			return None

		def mode_str_to_enum(input: str):
			input = input.replace("-", "_").upper()
			return (
				Environment[input] if input in Environment.__members__ else Environment.PRODUCTION
			)

		r.append(
			self.__check(
				v, "mode", validation_func=mode_validation, transform_func=mode_str_to_enum
			)
		)
		return r

	def _validate_all(
		self,
		v: dict[str, str],
		r: List[tuple[str, None | Any, str | bool]],
		type,
		ignore: bool = False,
		keys_length=0,
	) -> bool:
		key_require = [] * keys_length
		errors_msg = []
		for key_with_dot, value, err in r:
			key_require.append(key_with_dot)
			if err is True:
				setattr(self, key_with_dot.replace(".", "__"), value)
				continue
			elif err is False:
				if ignore is True:
					continue
				elif hasattr(self, key_with_dot):
					self_value = getattr(self, key_with_dot)
					if isinstance(self_value, str) and self_value != "":
						continue
					elif isinstance(self_value, int) and self_value != 0:
						continue
				self.logger.warning(f"'{key_with_dot}' in {type} is not set")
				continue
			errors_msg.append(f"'{key_with_dot}' with value '{value}' : {err}")

		if not ignore:
			preprocessed_values = [result.replace("__", ".") for result in v]
			key_not_used = [
				result for result in preprocessed_values if result not in set(key_require)
			]

			if len(key_not_used) != 0:
				self.logger.warning(
					"Keys '%s' in %s configuration are not used", ", ".join(key_not_used), type
				)

		if len(errors_msg) == 0:
			return True

		full_error = "Unable to validate %s configuration : \n- %s" % (
			type,
			"\n- ".join(errors_msg),
		)
		if ignore is True:
			self.logger.warning(full_error)
			return True
		self.logger.critical(full_error)
		return False

	def __check(
		self,
		raw_values: dict[str, str],
		key_with_dot: str,
		regex_pattern: Optional[str] = None,
		validation_func: Optional[Callable[[str], str | None]] = None,
		transform_func: Optional[Callable[[str], Any]] = None,
		is_path: bool = False,
		is_int: bool = False,
		is_positive_int: bool = True,
	) -> tuple[str, Optional[Any], str | bool]:
		real_key = key_with_dot.replace(".", "__")
		value = raw_values.get(real_key)

		if value is None:
			return key_with_dot, None, False

		try:
			if validation_func is not None:
				result = validation_func(value)
				if result is not None:
					return key_with_dot, value, result

			if transform_func:
				value = transform_func(value)
			elif is_int:
				value = int(value)
				if is_positive_int and value < 0:
					return key_with_dot, value, "It's not a positive number"
			elif is_path:
				if not os.path.exists(value):
					return key_with_dot, value, "Path didn't exist"
			elif regex_pattern is not None and not re.match(regex_pattern, str(value)):
				return key_with_dot, value, "Invalid format"
		except ValueError as e:
			return key_with_dot, value, f"{str(e)}"

		return key_with_dot, value, True
