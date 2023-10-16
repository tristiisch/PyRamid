
import yaml

class Config:
	def __init__(self):
		self.deezer_arl : str
		self.deezer_folder : str
		self.discord_token : str
		self.discord_ffmpeg : str

	def load(self):
		config_file_path = "config.yml"

		with open(config_file_path, "r") as config_file:
			config_data = yaml.safe_load(config_file)

		self.deezer_arl = config_data['deezer']['arl']
		self.deezer_folder = config_data['deezer']['folder']
		self.discord_token = config_data['discord']['token']
		self.discord_ffmpeg = config_data['discord']['ffmpeg']