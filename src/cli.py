import argparse

from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.client.client import SocketClient
from pyramid.client.requests.health import HealthRequest
from pyramid.tools.logs_handler import LogsHandler

info = ApplicationInfo()

logs_handler = LogsHandler()
logs_handler.log_to_console()

parser = argparse.ArgumentParser(description="Readme at https://github.com/tristiisch/PyRamid")
parser.add_argument("--version", action="store_true", help="Print version", required=False)
parser.add_argument("--git", action="store_true", help="Print git informations", required=False)
# parser.add_argument("--health", action="store_true", help="Print health", required=False)

health_subparser = parser.add_subparsers(dest="health")
health_parser = health_subparser.add_parser("health", help="Print health")
health_parser.add_argument(
	"--host", type=str, help="Specify the host for health check", required=False
)
health_parser.add_argument(
	"--port", type=int, help="Specify the port for health check", required=False
)

args = parser.parse_args()

if args.version:
	info.load_git_info()
	print(info.to_json())

elif args.git:
	info.load_git_info()
	print(info.git_info.to_json())

elif args.health:
	sc = SocketClient(args.host, args.port)
	health = HealthRequest()
	sc.send(health)

else:
	parser.print_help()
