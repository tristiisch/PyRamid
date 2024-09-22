import argparse

from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.client.client import SocketClient
from pyramid.client.requests.health import HealthRequest
from pyramid.tools.logs_handler import LogsHandler

def startup_cli():
	info = ApplicationInfo()

	parser = argparse.ArgumentParser(description="Readme at https://github.com/tristiisch/PyRamid")
	parser.add_argument("--version", action="store_true", help="Print version", required=False)

	health_subparser = parser.add_subparsers(dest="health")
	health_parser = health_subparser.add_parser("health", help="Check health status")
	health_parser.add_argument(
		"--host", type=str, help="Specify the host for health check", required=False
	)
	health_parser.add_argument(
		"--port", type=int, help="Specify the port for health check", required=False
	)

	args = parser.parse_args()

	if args.version:
		print(info.get_version())

	elif args.health:
		sc = SocketClient(args.host, args.port)
		health = HealthRequest()
		sc.send(health)

	else:
		parser.print_help()

if __name__ == "__main__":
	startup_cli()
