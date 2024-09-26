from abc import abstractmethod
from typing import Any

# from pyramid.client.common import SocketHeader
from pyramid.client.a_socket import ASocket
from pyramid.client.requests.ask_request import AskRequest
from pyramid.client.responses.a_response_header import ResponseHeader


class ARequest(ASocket):
	def __init__(self, data: AskRequest) -> None:
		self.ask = data
		# self.header = SocketHeader(self.__class__)

	@abstractmethod
	def load_data(self, data) -> Any:
		pass

	@abstractmethod
	def client_receive(self, header: ResponseHeader, data: Any) -> bool:
		pass
