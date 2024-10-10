

from logging import Logger
from discord import Guild

from pyramid.api.services.source_service import ISourceService
from pyramid.connector.discord.guild_cmd import GuildCmd
from pyramid.connector.discord.music_queue import MusicQueue
from pyramid.connector.discord.music.player_interface import MusicPlayerInterface
from pyramid.data.guild_data import GuildData


class GuildInstances:
	def __init__(self, guild: Guild, logger: Logger, source_service: ISourceService, ffmpeg_path: str):
		self.data = GuildData(guild, source_service)
		self.mpi = MusicPlayerInterface(self.data.guild.preferred_locale, self.data.track_list)
		self.songs = MusicQueue(self.data, ffmpeg_path, self.mpi)
		self.cmds = GuildCmd(logger, self.data, self.songs, source_service)
		self.mpi.set_queue_action(self.cmds)
