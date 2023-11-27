import json
import logging
import sys
from client.requests.a_request import ARequest
from client.requests.ask_request import AskRequest
from client.responses.a_response import ResponseHeader
from data.health import HealthModules


class HealthRequest(ARequest):
	def __init__(self) -> None:
		super().__init__(AskRequest("health"))

	def load_data(self, **data) -> HealthModules:
		return HealthModules(**data)

	def client_receive(self, header: ResponseHeader, data: HealthModules):
		data_json = json.dumps(data.__dict__, indent=4)

		if not data.is_ok():
			logging.warn("Health check failed")
			print(data_json)
			sys.exit(1)
		else:
			logging.info("Health check valid")
			print(data_json)
			sys.exit(0)
