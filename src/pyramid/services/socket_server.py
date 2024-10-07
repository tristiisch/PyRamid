import asyncio
import socket
from socket import socket as sock
from typing import Any

from pyramid.api.services.logger import ILoggerService
from pyramid.api.services.socket_server import ISocketServerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.client.common import ResponseCode, SocketCommon
from pyramid.client.requests.ask_request import AskRequest
from pyramid.client.responses.a_response import SocketResponse
from pyramid.data.ping import PingSocket

@pyramid_service(interface=ISocketServerService)
class SocketServerService(ISocketServerService, ServiceInjector):

	def __init__(self) -> None:
		self.__common = SocketCommon()
		self.__host = "0.0.0.0"
		self.__port = self.__common.port
		self.is_running = False
		self.server_socket: sock | None = None

	def injectService(self,
			logger_service: ILoggerService
		):
		self.__logger = logger_service

	async def open(self):
		self.server_socket = sock(socket.AF_INET, socket.SOCK_STREAM)
		# self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((self.__host, self.__port))
		self.server_socket.listen(10)

		self.__logger.info("Socket server open on %s:%d", self.__host, self.__port)

		self.is_running = True
		client_socket: sock | None = None
		client_address: Any = None
		client_ip: Any = None
		client_port: Any = None

		while self.is_running:
			try:
				client_socket, client_address = self.server_socket.accept()
				client_ip = client_address[0]
				client_port = client_address[1]
				response_to_send = await self.__handle_client(client_socket, client_ip, client_port)
				if response_to_send:
					# Convert the response data to JSON
					response_json = SocketCommon.serialize(
						response_to_send.to_json(SocketCommon.serialize)
					)

					# Send the JSON response back to the client
					# self.__logger.debug("[%s:%d] <- %s", client_ip, client_port, response_json)
					self.__common.send_chunk(client_socket, response_json)
			except Exception as err:
				if isinstance(err, OSError):
					if err.errno == 9:
						self.__logger.warning("Socket: [Errno 9] Bad file descriptor")
						continue
				if client_ip is not None and client_port is not None:
					self.__logger.warning("[%s:%d] %s", client_ip, client_port, err, exc_info=True)
			finally:
				if client_socket is not None:
					client_socket.close()
				client_socket = None
				client_address = None
				client_ip = None
				client_port = None
		self.__logger.info("Socket server closed")

	def close(self):
		self.is_running = False
		if self.server_socket is None:
			return
		# self.server_socket.shutdown(socket.SHUT_RDWR)
		self.server_socket.close()
		self.server_socket = None
		self.__logger.info("Socket server stop")

	async def __handle_client(self, client_socket: sock, client_ip, client_port) -> SocketResponse | None:
		data = self.__common.receive_chunk(client_socket)

		if not data:
			self.__logger.info("[%s:%d] -> <empty>", client_ip, client_port)
			return

		def object_hook(json):
			if isinstance(json, dict):
				return AskRequest(**json)
			return json

		json_data: AskRequest = SocketCommon.deserialize(data, object_hook=object_hook)

		response = SocketResponse()

		if not json_data.action:
			response.create(ResponseCode.ERROR, "Missing action field in JSON data")
			return response

		if json_data.action == "health":
			data = PingSocket(True)
			response.create(ResponseCode.OK, None, data)
			return response

		response.create(ResponseCode.ERROR, "Unknown action")
		self.__logger.info(
			"[%s:%d] <- Unknown action '%s'", client_ip, client_port, json_data.action
		)
		return response
