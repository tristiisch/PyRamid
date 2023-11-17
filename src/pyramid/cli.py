import argparse

from data.functional.application_info import ApplicationInfo

info = ApplicationInfo()

parser = argparse.ArgumentParser(description="Readme at https://github.com/tristiisch/PyRamid")
parser.add_argument("--version", action="store_true", help="Print version", required=False)
parser.add_argument("--git", action="store_true", help="Print git informations", required=False)
args = parser.parse_args()

if args.version:
	info.load_git_info()
	print(info.to_json())

elif args.git:
	info.load_git_info()
	print(info.git_info.to_json())

else:
	parser.print_help()
