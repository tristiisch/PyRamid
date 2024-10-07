from pyramid.api.services.message_queue import IMessageQueueService
from pyramid.api.tasks.tools.annotation import pyramid_task
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask


@pyramid_task(parameters=ParametersTask())
class MessageQueueTask(TaskInjector):

	def injectService(self, __message_queue_service: IMessageQueueService):
		self.__message_queue_service = __message_queue_service

	async def worker_asyc(self):
		await self.__message_queue_service.worker()

	async def stop_asyc(self):
		self.__message_queue_service.stop()
