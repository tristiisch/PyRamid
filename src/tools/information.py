import json
import platform
import subprocess

from tools.git import GitInfo


class ProgramInformation:
	def __init__(self):
		self.name = "pyramid"
		self.os = get_os().lower()
		self.version = "0.1.3"
		self.git_info = GitInfo()

	def load_git_info(self):
		git_info = GitInfo.read()
		if git_info is not None:
			self.git_info = git_info
		else:
			self.git_info.get()

	def get_version(self):
		return f"v{self.version}"

	def get_full_version(self):
		return f"v{self.version}-{self.git_info.commit_id}"

	def __str__(self):
		return f"{self.name.capitalize()} {self.get_full_version()} on {self.os} by {self.git_info.last_author}"

	def to_json(self):
		data = vars(self)
		data["git_info"] = vars(self.git_info)
		return json.dumps(data, indent=4)


def get_os() -> str:
	os_name = platform.system()
	if os_name == "Linux":
		return __get_linux_distro()
	elif os_name == "Windows":
		return f"{os_name}_{platform.version()}"
	elif os_name == "Darwin":
		return f"{os_name}_{platform.mac_ver()[0]}"
	else:
		return os_name


def __get_linux_distro() -> str:
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
				return "Linux distribution information not available."
		except FileNotFoundError:
			return "Linux distribution information not available."
