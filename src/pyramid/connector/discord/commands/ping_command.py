import math
from typing import Union
from discord import Interaction
from discord.app_commands import locale_str
from pyramid.connector.discord.commands.abstract_command import AbstractCommand

class PingCommand(AbstractCommand):

	def description(self) -> Union[str, locale_str]:
		return "Displays response time between bot and Discord API"

	async def execute(self, ctx: Interaction):
		await ctx.response.defer(thinking=True)
		latency = math.trunc(self.bot.latency * 1000)
		await ctx.followup.send("Pong ! (%dms)" % latency)
