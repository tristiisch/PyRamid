from deezer_api.search import DeezerSearch
import tools.utils
import os
import argparse

from setuptools import setup
from datetime import datetime
from tools.config import Config
from discord.bot import DiscordBot
from deezer_api.downloader import DeezerDownloader
from spotify.search import SpotifySearch

# Program information
NAME = "pyramid"
VERSION = "0.1.0"

# Argument management
parser = argparse.ArgumentParser(description="Music Bot Discord using Deezer.")
parser.add_argument("--version", action="store_true", help="Print version", required=False)
args = parser.parse_args()

if args.version:
    print(f"{NAME} v{VERSION}")
    exit(1)

# Logs management
current_datetime = datetime.now()
log_dir = "./logs"
log_name = f"./{current_datetime.strftime('%Y_%m_%d %H_%M')}.log"
# Deletion of log files over 10 
tools.utils.keep_latest_files(log_dir, 10)
logs_handler = tools.utils.create_logger(os.path.join(log_dir, log_name))

# Config load
config = Config()
config.load()

# Songs folder clear
tools.utils.clear_directory(config.deezer_folder)

# spotify_search = SpotifySongSearch(config.spotify_client_id, config.spotify_client_secret)
# res = spotify_search.search_songs("Jul C'est quand qu'il s'éteint ?", limit=10)
# if res != None:
# 	for track in res:
# 		print(track)

# deezer_search = DeezerSearch()

# res = deezer_search.search_track("Jul C'est quand qu'il s'éteint ?")

# Create Deezer player instance
deezer_dl = DeezerDownloader(config.deezer_arl, config.deezer_folder)

# Discord Bot Instance
discord_bot = DiscordBot(config, deezer_dl)
# Create bot
discord_bot.create()
# Connect bot to Discord servers
discord_bot.start(logs_handler)
