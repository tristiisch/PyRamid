
import platform
import subprocess
import pathlib

class ProgramInformation:
	def __init__(self):
		self.name = "pyramid"
		self.os = get_os().lower()
		self.version = "0.1.0"
		self.git_commit = get_git_revision()

	def get_version(self):
		return f"v{self.version}"
	 
	def __str__(self):
		return f"{self.name.capitalize()} v{self.version}-{self.git_commit} on {self.os}"
	 
def get_os() -> str:
	os_name = platform.system()
	if os_name == 'Linux':
		try:
			dist_name = subprocess.check_output(['lsb_release', '-i', '-s']).strip().decode('utf-8')
			dist_version = subprocess.check_output(['lsb_release', '-r', '-s']).strip().decode('utf-8')
			return f"{dist_name}_{dist_version}"
		except FileNotFoundError:
			try:
				with open('/etc/os-release', 'r') as f:
					lines = f.readlines()
					for line in lines:
						if line.startswith('PRETTY_NAME'):
							dist_info = line.split('=')[1].strip().strip('"')
							return f"Linux Distribution: {dist_info}"
					return "Linux distribution information not available."
			except FileNotFoundError:
				return "Linux distribution information not available."
	elif os_name == 'Windows':
		return f"{os_name}_{platform.version()}"
	elif os_name == 'Darwin':
		return f"{os_name}_{platform.mac_ver()[0]}"
	else:
		return os_name


def get_git_revision(base_path = None, max_lenght = 8):
	if not base_path:
		dir = pathlib.Path()
	else:
		dir =pathlib.Path(base_path)

	git_dir = dir / '.git'
	with (git_dir / 'HEAD').open('r') as head:
		ref = head.readline().split(' ')[-1].strip()

	with (git_dir / ref).open('r') as git_hash:
		return git_hash.readline().strip()[:max_lenght]
