import json
import logging
import sys
from pyramid.client.requests.a_request import ARequest
from pyramid.client.requests.ask_request import AskRequest
from pyramid.client.responses.a_response_header import ResponseHeader
from pyramid.data.ping import PingSocket


class PingRequest(ARequest):
	def __init__(self) -> None:
		super().__init__(AskRequest("health"))

	def load_data(self, **data) -> PingSocket:
		return PingSocket(**data)

	def client_receive(self, header: ResponseHeader, data: PingSocket) -> bool:
		data_json = json.dumps(data.__dict__, indent=4)

		if not data.is_ok():
			logging.warning("Health check failed")
			print(data_json)
			return False
		logging.info("Health check valid")
		print(data_json)
		return True
