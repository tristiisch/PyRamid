import json
from enum import Enum
from socket import socket as sock


# class SocketHeader:
# 	def __init__(self, cls: type) -> None:
# 		self.serialize = f"{cls.__module__}.{cls.__name__}"


class SocketCommon:
	def __init__(self):
		self.port = 49150
		self.buffer_size = 1024

	def receive_chunk(self, client_socket: sock):
		received_data = b""

		# while True:
		# 	data_chunk = client_socket.recv(self.buffer_size)
		# 	if not data_chunk:
		# 		break
		# 	received_data += data_chunk

		received_data = client_socket.recv(self.buffer_size)

		if not received_data:
			return None
		return received_data.decode("utf-8")

	@classmethod
	def send_chunk(cls, client_socket: sock, response: str):
		# for chunk in [
		# 	response[i : i + self.buffer_size] for i in range(0, len(response), self.buffer_size)
		# ]:
		# 	client_socket.send(chunk.encode("utf-8"))
		client_socket.send(response.encode("utf-8"))

	@classmethod
	def serialize(cls, obj):
		def default(obj):
			if hasattr(obj, "__dict__"):
				# if isinstance(obj, SocketResponse):
				return obj.__dict__
				# return {key: default(value) for key, value in obj.__dict__.items()}
			else:
				return obj

		return json.dumps(obj, default=default)

	@classmethod
	def deserialize(cls, obj: str, object_hook=None):
		return json.loads(obj, object_hook=object_hook)


class ResponseCode(Enum):
	OK = 200
	OK_EMPTY = 204
	EXCEPTION = 500
	ERROR = 501

	@classmethod
	def get_by_value(cls, value):
		for enum_member in cls:
			if enum_member.value == value:
				return enum_member
		raise ValueError(f"No {cls.__name__} member with value {value}")
