
from typing import Dict
from discord import Guild, VoiceClient
from tools.abc import ASearch

from tools.object import TrackList

class GuildData:
	def __init__(self, guild : Guild, search_engines: Dict[str, ASearch]):
		self.guild : Guild = guild
		self.track_list: TrackList = TrackList()
		self.voice_client: VoiceClient = None # type: ignore
		self.search_engines = search_engines
		self.search_engine = self.search_engines["deezer"]