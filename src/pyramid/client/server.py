import logging
import socket
from logging import Logger
from socket import socket as sock
from typing import Any

from client.common import ResponseCode, SocketCommon
from client.requests.ask_request import AskRequest
from client.responses.a_response import SocketResponse
from data.health import HealthModules

# from _socket import _RetAddress


class SocketServer:
	def __init__(self, logger: Logger, health: HealthModules, host: str = "0.0.0.0") -> None:
		self.__common = SocketCommon()
		self.__host = host
		self.__port = self.__common.port
		self.__health = health
		if logger:
			self.__logger = logger
		else:
			logger = logging.getLogger("socket")

	def start_server(self):
		# Set the host and port for the socket server

		# Create a socket object
		server_socket = sock(socket.AF_INET, socket.SOCK_STREAM)
		# Bind the socket to a specific address and port
		server_socket.bind((self.__host, self.__port))
		# Listen for incoming connections (up to x connections in the queue)
		server_socket.listen(10)

		self.__logger.info("Socket server open on %s:%d", self.__host, self.__port)

		client_socket: sock
		client_address: Any
		while True:
			# Wait for a connection from a client
			client_socket, client_address = server_socket.accept()
			client_ip = client_address[0]
			client_port = client_address[1]
			# self.__logger.debug("[%s:%d] accepted", client_ip, client_port)

			try:
				response_to_send = self.handle_client(client_socket, client_ip, client_port)

				if response_to_send:
					# Convert the response data to JSON
					response_json = self.__common.serialize(response_to_send.to_json(self.__common.serialize))

					# Send the JSON response back to the client
					# self.__logger.debug("[%s:%d] <- %s", client_ip, client_port, response_json)
					self.__common.send_chunk(client_socket, response_json)
			except Exception as err:
				self.__logger.warning("[%s:%d] %s", client_ip, client_port, err, exc_info=True)
			finally:
				client_socket.close()

	def handle_client(self, client_socket: sock, client_ip, client_port) -> SocketResponse | None:
		# Receive data from the client
		data = self.__common.receive_chunk(client_socket)

		if not data:
			self.__logger.info("[%s:%d] -> <empty>", client_ip, client_port)
			return

		# self.__logger.debug("[%s:%d] -> %s", client_ip, client_port, data)

		def object_hook(json):
			if isinstance(json, dict):
				return AskRequest(**json)
			return json

		json_data: AskRequest = self.__common.deserialize(data, object_hook=object_hook)

		response = SocketResponse()

		# Check the content of the JSON data
		if not json_data.action:
			response.create(ResponseCode.ERROR, "Missing action field in JSON data")
			return response

		if json_data.action == "health":
			data = self.__health
			response.create(ResponseCode.OK, None, data)
			return response

		# If the action is unknown, respond with an error message
		response.create(ResponseCode.ERROR, "Unknown action")
		self.__logger.info("[%s:%d] <- Unknown action '%s'", client_ip, client_port, json_data.action)
		return response
