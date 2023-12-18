from discord import Guild, VoiceClient

from data.tracklist import TrackList
from data.functional.engine_source import EngineSource


class GuildData:
	def __init__(self, guild: Guild, engine_source: EngineSource):
		self.guild: Guild = guild
		self.track_list: TrackList = TrackList()
		self.voice_client: VoiceClient = None  # type: ignore
		self.search_engine = engine_source
