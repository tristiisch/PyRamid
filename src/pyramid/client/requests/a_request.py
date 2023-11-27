from abc import abstractmethod
from typing import Any

# from client.common import SocketHeader
from client.responses.a_response import ResponseHeader
from client.a_socket import ASocket
from client.requests.ask_request import AskRequest


class ARequest(ASocket):
	def __init__(self, data: AskRequest) -> None:
		self.ask = data
		# self.header = SocketHeader(self.__class__)

	@abstractmethod
	def load_data(self, data) -> Any:
		pass

	@abstractmethod
	def client_receive(self, header: ResponseHeader, data: Any):
		pass
