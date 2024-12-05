import math
from discord import Interaction
from pyramid.connector.discord.commands.tools.abc import AbstractCommand
from pyramid.connector.discord.commands.tools.annotation import discord_command
from pyramid.connector.discord.commands.tools.parameters import ParametersCommand

@discord_command(parameters=ParametersCommand(description="Displays response time between bot and Discord API"))
class PingCommand(AbstractCommand):

	async def execute(self, ctx: Interaction):
		await ctx.response.defer(thinking=True)
		latency = math.trunc(self.bot.latency * 1000)
		await ctx.followup.send("Pong ! (%dms)" % latency)
