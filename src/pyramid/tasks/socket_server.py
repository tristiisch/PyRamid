from pyramid.api.services.socket_server import ISocketServerService
from pyramid.api.tasks.tools.annotation import pyramid_task
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask


@pyramid_task(parameters=ParametersTask())
class SocketServerTask(TaskInjector):

	def injectService(self, socket_service: ISocketServerService):
		self.__socket_server = socket_service

	async def worker_asyc(self):
		await self.__socket_server.open()

	async def stop_asyc(self):
		self.__socket_server.close()
