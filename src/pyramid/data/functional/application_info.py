import json
import os
import platform
import subprocess


class ApplicationInfo:
	def __init__(self):
		self.__name = "pyramid"
		self.__os = self.__detect_os().lower()
		self.__version = os.getenv("PROJECT_VERSION")

	def get_name(self):
		return self.__name.capitalize()

	def get_version(self):
		return f"v{self.__version}"

	def get_os(self):
		return self.__os

	def __detect_os(self) -> str:
		os_name = platform.system()
		if os_name == "Linux":
			return self.__detect_linux_distro()
		elif os_name == "Windows":
			return f"{os_name}_{platform.version()}"
		elif os_name == "Darwin":
			return f"{os_name}_{platform.mac_ver()[0]}"
		else:
			return os_name

	def __detect_linux_distro(self) -> str:
		try:
			dist_name = subprocess.check_output(["lsb_release", "-i", "-s"]).strip().decode("utf-8")
			dist_version = subprocess.check_output(["lsb_release", "-r", "-s"]).strip().decode("utf-8")
			return f"{dist_name}_{dist_version}"
		except FileNotFoundError:
			try:
				with open("/etc/os-release", "r") as f:
					lines = f.readlines()
					for line in lines:
						if line.startswith("PRETTY_NAME"):
							dist_info = line.split("=")[1].strip().strip('"')
							return dist_info
			except FileNotFoundError:
				pass
			return "Linux distribution information not available."
