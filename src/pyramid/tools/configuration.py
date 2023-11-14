import os

import yaml

from data.environment import Environment


class Configuration:
	def __init__(self):
		self.deezer_arl: str
		self.deezer_folder: str
		self.discord_token: str
		self.discord_ffmpeg: str
		self.spotify_client_id: str
		self.spotify_client_secret: str
		self.mode: Environment
		self.config_version: str

	def load(self):
		config_file_path = "config.yml"

		try:
			with open(config_file_path, "r") as config_file:
				config_data: dict = yaml.safe_load(config_file)
		except FileNotFoundError as err:
			raise err

		self.deezer_arl = config_data.get("deezer", {}).get("arl", "")
		self.deezer_folder = config_data.get("deezer", {}).get("folder", "")
		self.discord_token = config_data.get("discord", {}).get("token", "")

		ffmpeg = config_data.get("discord", {}).get("ffmpeg", "")
		if not os.path.exists(ffmpeg):
			raise Exception(f"Binary {ffmpeg} doesn't exist on this system")
		self.discord_ffmpeg = ffmpeg

		self.spotify_client_id = config_data.get("spotify", {}).get("client_id", "")
		self.spotify_client_secret = config_data.get("spotify", {}).get("client_secret", "")

		mode_upper = str(config_data.get("mode", "")).replace("-", "_").upper()
		self.mode = Environment[mode_upper] if mode_upper in Environment.__members__ else Environment.PRODUCTION

		self.config_version = config_data.get("version", "")
		self.default_limit_track = int(config_data.get("general", {}).get("default_limit_tracks", 0))
