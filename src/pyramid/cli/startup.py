import argparse
import sys

from pyramid.api.services.information import IInformationService
from pyramid.api.services.tools.tester import ServiceStandalone
from pyramid.client.client import SocketClient
from pyramid.client.requests.ping import PingRequest

def startup_cli():
	ServiceStandalone.import_services()

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
		information_service = ServiceStandalone.get_service(IInformationService)
		information = information_service.get()
		print(information.get_version())

	elif args.health:
		sc = SocketClient(args.host, args.port)
		health = PingRequest()
		result = sc.send(health)
		if result is not True:
			sys.exit(1)

	else:
		parser.print_help()
