import argparse
import re
import subprocess
import sys
from types import NoneType
from typing import List, Optional

requirement_file: str = "./requirements.txt"

class LibraryNotFoundException(Exception):
	pass

class PythonLibrary:
	def __init__(self, name: str, smallest_version_symbol: str, smallest_version: str,
				 biggest_version_symbol: Optional[str], biggest_version: Optional[str], extra: Optional[str]):
		self.Name = name
		self.Smallest_Version_Symbol = smallest_version_symbol
		self.Smallest_Version = smallest_version
		self.Biggest_Version_Symbol = biggest_version_symbol
		self.Biggest_Version = biggest_version
		self.Extra = extra

def install_requirement() -> bool:
	try:
		subprocess.run(["pip", "install", "--upgrade", "-r", requirement_file], check=True)
		return True
	except subprocess.CalledProcessError as err:
		print(f"Error: Unable to install requirements: {err}")
		return False

def add_lib(lib_name: str) -> bool:
	local_libs = get_local_libs()
	requirement_libs = get_requirement_libs()

	try:
		local = find_lib(local_libs, lib_name)
	except LibraryNotFoundException:
		local = None

	try:
		requirement = find_lib(requirement_libs, lib_name)
	except LibraryNotFoundException:
		requirement = None

	if local:
		print(f"Library {local.Name} is already installed on local files with version "
			  f"{local.Smallest_Version_Symbol} {local.Smallest_Version}", flush=True)
	else:
		subprocess.run(["pip", "install", lib_name])
		local_libs = get_local_libs()
		local = find_lib(local_libs, lib_name)

	if requirement:
		print(f"Library {requirement.Name} is already defined on {requirement_file} with version "
			  f"{requirement.Smallest_Version_Symbol} {requirement.Smallest_Version}", flush=True)
	else:
		format_requirement_lib(local)
		requirement_libs.append(local)
		save_libs(requirement_libs)

	return local is None or requirement is None 

def remove_lib(lib_name: str) -> bool:
	local_libs = get_local_libs()
	requirement_libs = get_requirement_libs()

	try:
		local = find_lib(local_libs, lib_name)
	except LibraryNotFoundException:
		local = None
	try:
		requirement = find_lib(requirement_libs, lib_name)
	except LibraryNotFoundException:
		requirement = None

	if not local:
		print(f"Library {lib_name} is not installed on local files.", flush=True)
	else:
		subprocess.run(["pip", "uninstall", "-y", local.Name])

		local_libs = get_local_libs()
		try:
			local = find_lib(local_libs, lib_name)
			print(f"Error: Failed to uninstall library '{lib_name}'.", flush=True)
			return False
		except LibraryNotFoundException:
			local = None

	if not requirement:
		print(f"Library {lib_name} is not defined on {requirement_file}.", flush=True)
	else:
		requirement_libs = [item for item in requirement_libs if item.Name != requirement.Name]
		save_libs(requirement_libs)
	return local is not None or requirement is not None

def update_libs() -> bool:
	result = install_requirement()
	if not result:
		return False
	requirement_libs = get_requirement_libs()
	local_requirement_libs = get_local_requirement_libs()
	requirement_libs_to_update = [
		item for item in requirement_libs
		if (local_lib := find_lib(local_requirement_libs, item.Name)) is not NoneType
		and local_lib.Smallest_Version != item.Smallest_Version
	]

	if not requirement_libs_to_update:
		print("There is no update", flush=True)
		return True

	result = True
	print("Libraries updated:", flush=True)
	for requirement_lib_to_update in requirement_libs_to_update:
		try:
			local_lib = find_lib(local_requirement_libs, requirement_lib_to_update.Name)
			print(f"{requirement_lib_to_update.Name} {requirement_lib_to_update.Smallest_Version} -> {local_lib.Smallest_Version}")

			requirement_lib_to_update.Smallest_Version = local_lib.Smallest_Version
		except LibraryNotFoundException as e:
			print(f"Error updating library: {e}", flush=True)
			result = False

	if not result:
		return False

	save_libs(requirement_libs)
	return True

def get_libs(content: List[str]) -> List[PythonLibrary]:
	lib_objects = []
	regex = r"^(?P<name>[a-zA-Z0-9_.\-]+)(?P<smal_ver_symb>>=|==)(?P<smal_ver>[^,;\s]*)(,(?P<big_ver_symb><)(?P<big_ver>[^,;\s]*))?(\s*;\s*(?P<extra>.+))?$"

	for i, line in enumerate(content):
		if i == len(content) - 1 and not line.strip():  # Skip the last line if it's empty
			continue
		match = re.match(regex, line)
		if not match:
			print("Error: unknown line '" + line + "'")
			continue

		name = match.group("name")
		smal_ver_symb = match.group("smal_ver_symb")
		smal_ver = match.group("smal_ver")
		big_ver_symb = match.group("big_ver_symb")
		big_ver = match.group("big_ver")
		extra = match.group("extra")

		lib_object = PythonLibrary(name, smal_ver_symb, smal_ver, big_ver_symb, big_ver, extra)
		lib_objects.append(lib_object)

	return lib_objects


def save_libs(lib_objects: List[PythonLibrary]) -> None:
	data = [
		f"{lib.Name}{lib.Smallest_Version_Symbol}{lib.Smallest_Version}" +
		(f",{lib.Biggest_Version_Symbol}{lib.Biggest_Version}" if lib.Biggest_Version_Symbol else "") +
		(f"; {lib.Extra}" if lib.Extra else "")
		for lib in lib_objects
	]

	with open(requirement_file, "w") as file:
		file.write("\n".join(data))
		file.write("\n")
	print(f"Libraries saved to {requirement_file}")

def get_requirement_libs() -> List[PythonLibrary]:
	with open(requirement_file, "r") as file:
		lines = file.readlines()
	return get_libs(lines)

def get_local_libs() -> List[PythonLibrary]:
	result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
	lines = result.stdout.split("\n")
	return get_libs(lines)

def find_lib(lib_objects: List[PythonLibrary], lib_name: str) -> PythonLibrary:
	lib = next((item for item in lib_objects if item and lib_name.lower() == item.Name.lower()), None)
	if lib is None:
		raise LibraryNotFoundException(f"Library '{lib_name}' not found.")
	return lib

def find_libs(lib_objects: List[PythonLibrary], lib_objects2: List[PythonLibrary]) -> List[PythonLibrary]:
	result = []
	for item in lib_objects:
		try:
			if find_lib(lib_objects2, item.Name):
				result.append(item)
		except LibraryNotFoundException:
			result.append(None)
	return result

def get_local_requirement_libs() -> List[PythonLibrary]:
	local_libs = get_local_libs()
	requirement_libs = get_requirement_libs()
	local_requirement_libs = find_libs(local_libs, requirement_libs)

	return local_requirement_libs

def format_requirement_lib(lib_object: PythonLibrary) -> None:
	lib_object.Smallest_Version_Symbol = ">="

	higher_major_version = f"{int(lib_object.Smallest_Version.split('.')[0]) + 1}.0.0"
	lib_object.Biggest_Version_Symbol = "<"
	lib_object.Biggest_Version = higher_major_version

def parse_arguments():
	parser = argparse.ArgumentParser(description="Manage Python libraries")
	parser.add_argument("--install", action="store_true", help="Install libraries from requirements file")
	parser.add_argument("--remove", metavar="<name>", help="Remove a library by name")
	parser.add_argument("--update", action="store_true", help="Update libraries to their latest versions")
	parser.add_argument("--add", metavar="<name>", help="Add a library by name")
	return parser.parse_args()

def main():
	args = parse_arguments()
	result = True

	if args.install:
		result = install_requirement()
	elif args.remove:
		result = remove_lib(args.remove)
	elif args.update:
		result = update_libs()
	elif args.add:
		result = add_lib(args.add)
	else:
		print("No action specified. Use --help for usage information.")
		return

	if not result:
		sys.exit(1)

if __name__ == "__main__":
	main()
