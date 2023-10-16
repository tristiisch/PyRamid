
import tools.utils
from datetime import datetime

from tools.config import Config
from discord.bot import DiscordBot
from deezer.downloader import DeezerDownloader

current_datetime = datetime.now()

file_name = f"./logs/{current_datetime.strftime('%Y_%m_%d %H_%M')}.log"
logs_handler = tools.utils.create_logger(file_name)

config = Config()
config.load()

deezer_dl = DeezerDownloader(config.deezer_arl, config.deezer_folder)

discord_bot = DiscordBot(config.discord_token, config.discord_ffmpeg, deezer_dl)
discord_bot.create()
discord_bot.start(logs_handler)
