from typing import Self
from pyramid.api.services.configuration import IConfigurationService
from pyramid.data.environment import Environment
from pyramid.services.configuration import ConfigurationService

class ConfigurationBuilder():

    def __init__(self):
        self.service = ConfigurationService()

    def discord_token(self, discord_token: str) -> Self:
        self.service.discord__token = discord_token
        return self

    def discord_ffmpeg(self, discord_ffmpeg: str) -> Self:
        self.service.discord__ffmpeg = discord_ffmpeg
        return self

    def deezer_arl(self, deezer_arl: str) -> Self:
        self.service.deezer__arl = deezer_arl
        return self

    def deezer_folder(self, deezer_folder: str) -> Self:
        self.service.deezer__folder = deezer_folder
        return self

    def spotify_client_id(self, spotify_client_id: str) -> Self:
        self.service.spotify__client_id = spotify_client_id
        return self

    def spotify_client_secret(self, spotify_client_secret: str) -> Self:
        self.service.spotify__client_secret = spotify_client_secret
        return self

    def general_limit_tracks(self, limit_tracks: int) -> Self:
        self.service.general__limit_tracks = limit_tracks
        return self

    def mode(self, mode: Environment) -> Self:
        self.service.mode = mode
        return self

    def version(self, version: str) -> Self:
        self.service.version = version
        return self

    def build(self) -> IConfigurationService:
        return self.service
