from typing import Any, Self
from pyramid.client.a_socket import ASocket
from pyramid.client.common import ResponseCode, SocketCommon
from pyramid.client.responses.a_response_header import ResponseHeader
# from pyramid.client.common import ResponseCode, SocketHeader


class SocketResponse(ASocket):
	def __init__(
		self,
		data: Any | None = None,
		error_data: str | None = None,
		header: ResponseHeader | None = None,
	) -> None:
		super().__init__()
		self.header = header
		self.data = data
		self.error_data = error_data

	def create(
		self,
		code: ResponseCode,
		message: str | None,
		data: Any | None = None,
		error_data: str | None = None,
	) -> None:
		super().__init__()
		self.header = ResponseHeader(code, message)
		self.data = data
		self.error_data = error_data

	def to_json(self, serializer):
		return {
			"header": {"code": self.header.code.value, "message": self.header.message}
			if self.header
			else None,
			"data": serializer(self.data) if self.data else None,
			"error_data": serializer(self.error_data) if self.error_data else None,
		}

	@classmethod
	def from_str(cls, data: str) -> Self:
		json = SocketCommon.deserialize(data)
		self = cls.from_json(json)
		return self

	@classmethod
	def from_json(cls, json_dict: dict) -> Self:
		self: Self = cls()

		header_dict = json_dict.get("header")
		if header_dict:
			self.header = ResponseHeader(
				ResponseCode.get_by_value(header_dict.get("code")), header_dict.get("message")
			)

		self.data = json_dict.get("data")
		self.error_data = json_dict.get("error_data")

		return self
