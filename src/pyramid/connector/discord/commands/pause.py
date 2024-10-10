from discord import Guild, Interaction

from pyramid.api.services.discord import IDiscordService
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.annotation import discord_command
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued


@discord_command(parameters=ParametersCommand(
	description="Pauses the music",
	only_guild=True
))
class PauseCommand(AbstractCommand):

	def injectService(self,
			discord_service: IDiscordService
		):
		self.__discord_service = discord_service

	async def execute(self, ctx: Interaction):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		guild = ctx.guild
		if not guild:
			raise Exception("Command was not executed in a guild")
		guild_cmd = self.__discord_service.get_guild_cmd(guild)

		await guild_cmd.pause(ms, ctx)
