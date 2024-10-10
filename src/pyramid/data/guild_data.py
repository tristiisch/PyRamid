from discord import Guild, VoiceClient

from pyramid.api.services.source_service import ISourceService
from pyramid.data.tracklist import TrackList


class GuildData:
	def __init__(self, guild: Guild, source_service: ISourceService):
		self.guild: Guild = guild
		self.track_list: TrackList = TrackList()
		self.voice_client: VoiceClient = None  # type: ignore
		self.search_engine = source_service
