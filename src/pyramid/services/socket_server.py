
from threading import Thread

from pyramid.api.services import ILoggerService, ISocketServerService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.client.server import SocketServer
from pyramid.data.health import HealthModules


@pyramid_service(interface=ISocketServerService)
class SocketServerService(ISocketServerService, ServiceInjector):

	def __init__(self):
		pass

	def injectService(self, logger_service: ILoggerService):
		self.logger_service = logger_service

	def start(self):
		self._health = HealthModules()
		self._health.configuration = True
		self._health.discord = True

		self.socket_server = SocketServer(self.logger_service.getChild("socket"), self._health)
		thread = Thread(name="Socket", target=self.socket_server.start_server, daemon=True)
		thread.start()
