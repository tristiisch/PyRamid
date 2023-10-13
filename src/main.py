import yaml
from discord_bot import DiscordBot
from deezer_downloader import DeezerDownloader

config_file_path = "config.yml"

with open(config_file_path, "r") as config_file:
    config_data = yaml.safe_load(config_file)

deezer_arl = config_data['deezer']['arl']
deezer_folder = config_data['deezer']['folder']
discord_token = config_data['discord']['token']
discord_ffmpeg = config_data['discord']['ffmpeg']

# print("deezer_arl", deezer_arl)
# print("deezer_folder", deezer_folder)
# print("discord_token", discord_token)

deezer_dl = DeezerDownloader(deezer_arl, deezer_folder)
# deezer_dl.dl_track_by_name("Téléphone")

discord_bot = DiscordBot(discord_token, discord_ffmpeg, deezer_dl)
discord_bot.create()
discord_bot.start()