import logging
import socket
from client.responses.a_response import SocketResponse
from client.requests.a_request import ARequest

from client.common import SocketCommon


class SocketClient:
	def __init__(self, host: str | None=None, port: int | None=None) -> None:
		self.__common = SocketCommon()
		self.__host = host
		if not host:
			self.__host = "localhost"
		else:
			self.__host = host
		if not port:
			self.__port = self.__common.port
		else:
			self.__port = port
		self.__logger = logging.getLogger()

	def send(self, req: ARequest):
		# Create a socket object
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# Convert the request data to JSON
			json_request = self.__common.serialize(req.ask)

			# Connect to the server
			self.__logger.info("Connect to %s:%d", self.__host, self.__port)
			client_socket.connect((self.__host, self.__port))

			# Send the JSON request to the server
			self.__logger.info("Send '%s'", json_request)
			self.__common.send_chunk(client_socket, json_request)

			# Receive the response from the server
			response_str = self.__common.receive_chunk(client_socket)
			if not response_str:
				self.__logger.warning("Received empty request")
				return

			self.__logger.info("Received '%s'", response_str)
			self.receive(req, response_str)

		except Exception as err:
			self.__logger.warning(err)

		finally:
			# Close the client socket
			client_socket.close()

	def receive(self, action: ARequest, response_str: str):
		def object_hook(json):
			if not isinstance(json, dict):
				raise ValueError("Unable to deserialize '%s'" % json)

			if not isinstance(json, SocketResponse):
				print("debug", json)
				return SocketResponse.from_json(json)

			return json

		response: SocketResponse = SocketResponse.from_json(self.__common.deserialize(response_str))
		# response: SocketResponse = self.__common.deserialize(response_str, object_hook)
		# response: SocketResponse = SocketResponse(**response_json)
		if not response.header:
			raise ValueError("No header received")
		if not response.data:
			raise ValueError("No data received")

		response_data = action.load_data(**(self.__common.deserialize(response.data)))
		action.client_receive(response.header, response_data)
