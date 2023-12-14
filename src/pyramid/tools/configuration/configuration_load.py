import os
import re
from abc import ABC
from logging import Logger
from typing import Any, Callable, List, Optional

import yaml
from data.environment import Environment


class ConfigurationFromEnv(ABC):
	def _get_env_vars(self) -> dict[str, str]:
		# Load values from environment variables
		return {str(key).lower(): str(value) for key, value in os.environ.items()}


class ConfigurationFromYAML(ABC):
	def __init__(self, logger: Logger):
		self.__logger = logger

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
		raw_values[key] = config_values

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
				self.__logger.warning(f"'{key_with_dot}' in {type} is not set")
				continue
			errors_msg.append(f"'{key_with_dot}' with value '{value}' : {err}")

		if not ignore:
			preprocessed_values = [result.replace("__", ".") for result in v]
			key_not_used = [
				result for result in preprocessed_values if result not in set(key_require)
			]

			if len(key_not_used) != 0:
				self.__logger.warning(
					"Keys '%s' in %s configuration are not used", ", ".join(key_not_used), type
				)

		if len(errors_msg) == 0:
			return True

		full_error = "Unable to validate %s configuration : \n- %s" % (
			type,
			"\n- ".join(errors_msg),
		)
		if ignore is True:
			self.__logger.warning(full_error)
			return True
		self.__logger.critical(full_error)
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
