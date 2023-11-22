from abc import ABC
from enum import Enum
from typing import Any

import yaml


class ConfigurationToYAML(ABC):
	def _save_to_yaml(self, file_name: str):
		# Save the configuration to a YAML file
		with open(file_name, "w") as yaml_file:
			for section, data in self.__to_dict().items():
				# Check if the section has more than one key-value pair
				if isinstance(data, dict):
					yaml.dump({section: data}, yaml_file, default_flow_style=False)
					yaml_file.write("\n")  # Add an empty line between sections
				else:
					yaml.dump({section: data}, yaml_file, default_flow_style=False)

	def __flatten_dict(self, d: dict[str, Any], parent_key="", sep="."):
		"""
		Flatten a nested dictionary and separate keys with the specified separator.
		"""
		items = []
		for k, v in d.items():
			new_key = f"{parent_key}{sep}{k}" if parent_key else k
			if isinstance(v, dict):
				items.extend(self.__flatten_dict(v, new_key, sep=sep).items())
			else:
				items.append((new_key, v))
		return dict(items)

	def __to_dict(self):
		flat_dict = self.__flatten_dict(vars(self))
		nested_dict = {}
		for key, value in flat_dict.items():
			if key[0] == "_":
				continue  # Ignore privates attributes
			keys = key.split("__")

			if isinstance(value, Enum):
				value = value.name.lower()  # Convert Enum to its value
			current_level = nested_dict

			for k in keys[:-1]:
				current_level = current_level.setdefault(k, {})
			current_level[keys[-1]] = value
		return nested_dict
