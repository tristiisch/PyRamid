from abc import ABC, abstractmethod
from pyramid.connector.discord.bot import DiscordBot

class IDiscordService(ABC):

	def __init__(self):
		self.discord_bot: DiscordBot
