

from logging import Logger
from discord import Guild

from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.connector.discord.guild_queue import GuildQueue
from pyramid.connector.discord.music_player_interface import MusicPlayerInterface
from pyramid.data.functional.engine_source import EngineSource
from pyramid.data.guild_data import GuildData


class GuildInstances:
	def __init__(self, guild: Guild, logger: Logger, engine_source: EngineSource, ffmpeg_path: str):
		self.data = GuildData(guild, engine_source)
		self.mpi = MusicPlayerInterface(self.data.guild.preferred_locale, self.data.track_list)
		self.songs = GuildQueue(self.data, ffmpeg_path, self.mpi)
		self.cmds = GuildCmd(logger, self.data, self.songs, engine_source)
		self.mpi.set_queue_action(self.cmds)
