from pyramid.api.services.discord import IDiscordService
from pyramid.api.tasks.tools.annotation import pyramid_task
from pyramid.api.tasks.tools.injector import TaskInjector
from pyramid.api.tasks.tools.parameters import ParametersTask

@pyramid_task(parameters=ParametersTask())
class DiscordTask(TaskInjector):

	def __init__(self):
		pass

	def injectService(self,
			discord_service: IDiscordService
		):
		self.__discord_service = discord_service

	async def worker_asyc(self):
		self.discord_bot = self.__discord_service.discord_bot
		await self.discord_bot.start()

	async def stop_asyc(self):
		await self.discord_bot.stop()
