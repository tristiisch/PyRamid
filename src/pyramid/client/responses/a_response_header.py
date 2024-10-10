from typing import Any, Self
from pyramid.client.a_socket import ASocket
from pyramid.client.common import ResponseCode, SocketCommon
# from pyramid.client.common import ResponseCode, SocketHeader


# class ReponseHeader(SocketHeader):
class ResponseHeader:
	def __init__(self, code: ResponseCode, message: str | None) -> None:
		# super().__init__(self.__class__)
		self.code = code
		self.message = message
