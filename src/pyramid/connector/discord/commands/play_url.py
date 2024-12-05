from discord import Interaction

from pyramid.api.services.discord import IDiscordService
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.annotation import discord_command
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from pyramid.data.source_type import SourceType


@discord_command(parameters=ParametersCommand(
	description="Plays a track, artist, album, or playlist from a URL",
	only_guild=True
))
class PlayUrlCommand(AbstractCommand):

	def injectService(self,
			discord_service: IDiscordService
		):
		self.__discord_service = discord_service

	async def execute(self, ctx: Interaction, url: str):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		guild = ctx.guild
		if not guild:
			raise Exception("Command was not executed in a guild")
		guild_cmd = self.__discord_service.get_guild_cmd(guild)

		await guild_cmd.play_url(ms, ctx, url)
