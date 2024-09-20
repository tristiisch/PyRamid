from abc import ABC, abstractmethod
from discord import Guild
from discord.ext.commands import Bot

from pyramid.connector.discord.guild_cmd import GuildCmd

class IDiscordService(ABC):

	def __init__(self):
		self.bot: Bot

	@abstractmethod
	async def connect_bot(self):
		pass

	@abstractmethod
	async def disconnect_bot(self):
		pass

	@abstractmethod
	def get_guild_cmd(self, guild: Guild) -> GuildCmd:
		pass