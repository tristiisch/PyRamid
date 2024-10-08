from pyramid.api.services.discord import IDiscordService
from pyramid.api.tasks.tools.annotation import pyramid_task
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask

@pyramid_task(parameters=ParametersTask(stop_own_loop = True))
class DiscordTask(TaskInjector):

	def injectService(self, discord_service: IDiscordService):
		self.__discord_service = discord_service

	async def worker_asyc(self):
		await self.__discord_service.connect_bot()

	async def stop_asyc(self):
		await self.__discord_service.disconnect_bot()
