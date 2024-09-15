from abc import ABC
from pyramid.data.environment import Environment

class IConfigurationService(ABC):

	def __init__(self):
		self.discord__token: str = ""
		self.discord__ffmpeg: str = ""
		self.deezer__arl: str = ""
		self.deezer__folder: str = ""
		self.spotify__client_id: str = ""
		self.spotify__client_secret: str = ""
		self.general__limit_tracks: int = 0
		self.mode: Environment = Environment.PRODUCTION
		self.version: str = ""
