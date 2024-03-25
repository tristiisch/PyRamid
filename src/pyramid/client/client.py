import logging
import socket
from pyramid.client.responses.a_response import SocketResponse
from pyramid.client.requests.a_request import ARequest

from pyramid.client.common import SocketCommon


class SocketClient:
	def __init__(self, host: str | None = None, port: int | None = None) -> None:
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
		self._timeout = 5

	def send(self, req: ARequest) -> bool:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.settimeout(self._timeout)

		try:
			# Convert the request data to JSON
			json_request = self.__common.serialize(req.ask)

			# Connect to the server
			self.__logger.info("Connect to %s:%d", self.__host, self.__port)
			client_socket.connect((self.__host, self.__port))

			# Send the JSON request to the server
			self.__logger.debug("Send '%s'", json_request)
			self.__common.send_chunk(client_socket, json_request)

			# Receive the response from the server
			response_str = self.__common.receive_chunk(client_socket)
			if not response_str:
				self.__logger.warning("Received empty request")
				return False

			self.__logger.debug("Received '%s'", response_str)
			self.receive(req, response_str)
			return True

		except OverflowError:
			self.__logger.warning(
				"Invalid port format '%s'. Must be in range 0-65535.", self.__port
			)

		except socket.gaierror:
			self.__logger.warning("Invalid ip format '%s'", self.__host)

		except TimeoutError:
			self.__logger.warning(
				"Connection timed out after %d secs. No response has been received.", self._timeout
			)

		except OSError as err:
			self.__logger.warning(err)

		finally:
			client_socket.close()
		return False

	def receive(self, action: ARequest, response_str: str):
		response: SocketResponse = SocketResponse.from_json(self.__common.deserialize(response_str))

		if not response.header:
			raise ValueError("No header received")
		if not response.data:
			raise ValueError("No data received")

		response_data = action.load_data(**(self.__common.deserialize(response.data)))
		action.client_receive(response.header, response_data)
