import yaml

from tools.utils import Mode


class Config:
	def __init__(self):
		self.deezer_arl: str
		self.deezer_folder: str
		self.discord_token: str
		self.discord_ffmpeg: str
		self.spotify_client_id: str
		self.spotify_client_secret: str
		self.mode: Mode
		self.config_version: str

	def load(self):
		config_file_path = "config.yml"

		with open(config_file_path, "r") as config_file:
			config_data = yaml.safe_load(config_file)

		self.deezer_arl = config_data["deezer"]["arl"]
		self.deezer_folder = config_data["deezer"]["folder"]
		self.discord_token = config_data["discord"]["token"]
		self.discord_ffmpeg = config_data["discord"]["ffmpeg"]
		self.spotify_client_id = config_data["spotify"]["client_id"]
		self.spotify_client_secret = config_data["spotify"]["client_secret"]
		self.spotify_client_secret = config_data["spotify"]["client_secret"]

		mode_upper = str(config_data["mode"]).replace("-", "_").upper()
		for mode in Mode:
			if mode.name == mode_upper:
				self.mode = mode
				break
		else:
			self.mode = Mode.PRODUCTION

		self.config_version = config_data["version"]
