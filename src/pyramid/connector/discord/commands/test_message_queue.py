

from discord import Interaction

from pyramid.api.services.discord import IDiscordService
from pyramid.api.services.message_queue import IMessageQueueService
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.annotation import discord_command
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.message_queue_item import MessageQueueItem


@discord_command(parameters=ParametersCommand())
class TestMessageQueueCommand(AbstractCommand):

	def injectService(self,
			message_queue_service: IMessageQueueService
		):
		self.__message_queue_service = message_queue_service

	async def execute(self, ctx: Interaction, nb: int = 100, reuse: bool = False, priority: bool = False):
	# async def execute(self, ctx: Interaction, nb: int = 100, reuse: bool = False):
		await ctx.response.defer(thinking=True)

		id = None
		for i in range(1, nb + 1):
			if priority:
				id = self.__message_queue_service.add(MessageQueueItem(ctx.followup.send, ctx.client.loop, content=f"Priority n°{i}"), id, 1)
			else:
				id = self.__message_queue_service.add(MessageQueueItem(ctx.followup.send, ctx.client.loop, content=f"Hello n°{i}"), id)
			if not reuse:
				id = None
