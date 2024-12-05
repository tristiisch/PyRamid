import select
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
		self.server: sock | None = None
		self.connected_clients: set[sock] = set()

	def injectService(self,
			logger_service: ILoggerService
		):
		self.__logger = logger_service

	async def open(self):
		if self.is_running:
			self.__logger.warning("Socket server is already running.")
			return
		self.server = sock(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((self.__host, self.__port))
		self.server.listen(10)
		self.server.setblocking(False)
		self.is_running = True

		self.__logger.info("Socket server open on %s:%d", self.__host, self.__port)
		await self.__run()

	async def __run(self):
		if not self.server:
			return
		while self.is_running:
			client_socket: sock | None = None
			client_address: Any = None
			client_ip: Any = None
			client_port: Any = None
			response_to_send: SocketResponse | None = None
			response_json: str | None = None
			readable: list[sock]
			# readable, writable, exceptional = select.select([self.server, *self.connected_clients], [], [], None)
			self.__logger.debug("server.select")
			readable, writable, exceptional = select.select([self.server], [], [], None)
			self.__logger.debug("server.selected")

			if not self.is_socket_open(self.server):
				self.__logger.info("Socket server queue closed, stopping...")
				break
	
			if self.server in readable:
				try:
					self.__logger.debug("server.accept")
					client_socket, client_address = self.server.accept()
					self.__logger.debug("server.accepted")
					client_socket.setblocking(False)
					client_ip, client_port = client_address
					self.connected_clients.add(client_socket)
					self.__logger.debug("Client %s:%d connected", *client_address)

					await self.__handle_client(client_socket, client_ip, client_port)
				except Exception as err:
					if isinstance(err, OSError) and err.errno == 9:
						self.__logger.warning("Socket: [Errno 9] Bad file descriptor")
					elif client_ip is not None and client_port is not None:
						self.__logger.warning("[%s:%d] %s", client_ip, client_port, err, exc_info=True)
					else:
						raise err
				finally:
					if client_socket is not None:
						self.__logger.debug("Client %s:%d disconnected ", *client_address)
						self.connected_clients.discard(client_socket)
						client_socket.close()
		self.__logger.info("Socket server closed")

	def close(self):
		self.is_running = False
		if not self.server or not self.is_socket_open(self.server):
			self.__logger.warning("Socket server already stopped")
			return

		try:
			self.server.shutdown(socket.SHUT_RDWR)
		except OSError as err:
			if err.errno == 9:
				self.__logger.warning("Socket server already closed (Errno 9).")
			else:
				self.__logger.warning("Error during socket shutdown: %s", err)
			return
		self.server.close()

		for client in list(self.connected_clients):
			try:
				client.close()
			except Exception:
				pass
		self.connected_clients.clear()
		self.__logger.info("Socket server stopped")

	async def __handle_client(self, client_socket: sock, client_ip, client_port):
		try:
			data = self.__common.receive_chunk(client_socket)

			if not data:
				self.__logger.info("[%s:%d] -> <empty>", client_ip, client_port)
				self.connected_clients.remove(client_socket)
				client_socket.close()
				return
			response = await self.__process_request(data, client_ip, client_port)
			if response:
				response_json = SocketCommon.serialize(
					response.to_json(SocketCommon.serialize)
				)
				# Send the JSON response back to the client
				# self.__logger.debug("[%s:%d] <- %s", client_ip, client_port, response_json)
				self.__common.send_chunk(client_socket, response_json)

		except Exception as err:
			self.__logger.warning("Error handling client: %s", err)
			self.connected_clients.discard(client_socket)
			client_socket.close()

	async def __process_request(self, data: str, client_ip, client_port) -> SocketResponse | None:
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
			pingSocket = PingSocket(True)
			response.create(ResponseCode.OK, None, pingSocket)
			return response
		response.create(ResponseCode.ERROR, "Unknown action")
		self.__logger.info(
			"[%s:%d] <- Unknown action '%s'", client_ip, client_port, json_data.action
		)

	@classmethod
	def is_socket_open(cls, sock: sock):
		try:
			sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
			return True
		except socket.error:
			return False