import argparse
import os
import re

from pydeezer import Deezer
from pydeezer.constants import track_formats
from pathvalidate import sanitize_filepath

from datetime import datetime

class TrackMinimal:
	def __init__(self, data):
		self.id = data['id']
		self.author_name = data['artist']['name']
		self.author_picture = data['artist']['picture_medium']
		# self.authors =  [element['ART_NAME'] for element in data["ARTISTS"]]
		self.name = data['title_short']
		self.album_title = data['album']['title']
		self.album_picture = data['album']['cover_big']
		# self.duration_seconds = data['DURATION']
		# self.duration = self.__format_duration(data['DURATION'])
		# self.file_size = data['FILESIZE']
		# self.date = data["DATE_START"]
		# self.file_local = file_path

	def get_full_name(self) -> str :
		return f"{self.author_name} - {self.name}"
	
	def format_duration(self, input : str) -> str :
		seconds = int(input)

		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)

		time_format = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

		if days > 0:
			time_format = "{:02}d ".format(days) + time_format

		if days == 0 and hours == 0:
			time_format = "{:02}:{:02}".format(minutes, seconds)

		return time_format
	
	def _format_date(self, input : str) -> str :
		date_object = datetime.strptime(input, "%Y-%m-%d")

		return date_object.strftime("%x")
		

class Track(TrackMinimal):
	def __init__(self, data, file_path):
		self.author_name = data['ART_NAME']
		self.author_picture = f"https://e-cdn-images.dzcdn.net/images/artist/{data['ART_PICTURE']}/512x512-000000-80-0-0.jpg"
		self.authors =  [element['ART_NAME'] for element in data["ARTISTS"]]
		self.name = data['SNG_TITLE']
		self.album_title = data['ALB_TITLE']
		self.album_picture = f"https://e-cdn-images.dzcdn.net/images/cover/{data['ALB_PICTURE']}/512x512-000000-80-0-0.jpg"
		self.actual_seconds = int(0)
		self.duration_seconds = int(data['DURATION'])
		self.duration = self.format_duration(data['DURATION'])
		self.file_size = data['FILESIZE']
		self.date = self._format_date(data["PHYSICAL_RELEASE_DATE"])
		self.file_local = file_path


class DeezerDownloader:
	def __init__(self, arl, folder):
		self.deezer_api = Deezer(arl)
		self.folder_path = folder
		self.music_format = track_formats.MP3_128

	def get_track_by_name(self, name) -> TrackMinimal:
		tracks_found = self.deezer_api.search_tracks(name)
		if not tracks_found:
			print(f"Track '{name}' not found")
			return None
		# title = tracksFound[0]['title']
		track = TrackMinimal(tracks_found[0])
		return track

	def dl_track_by_id(self, track_id) -> Track:
		track_to_dl = self.deezer_api.get_track(track_id)
		if not track_to_dl:
			print('Error')
		file_name = sanitize_filepath(f"{track_to_dl['info']['DATA']['ART_NAME']} - {track_to_dl['info']['DATA']['SNG_TITLE']}")
		track_to_dl['download'](self.folder_path, filename=file_name, quality=self.music_format, with_lyrics=False)
		# self.__rename_song(title.replace("%20", " "), id)
		# print('Done')
		track_downloaded = Track(track_to_dl['info']['DATA'], os.path.join(self.folder_path, file_name) + ".mp3")
		return track_downloaded

	def dl_track_by_name(self, name) -> Track:
		tracks_found = self.deezer_api.search_tracks(name)
		if not tracks_found:
			return print('Error')
		# title = tracksFound[0]['title']
		track_downloaded = self.dl_track_by_id(tracks_found[0]['id'])
		return track_downloaded

	def __rename_song(self, song_title, song_id):
		formated_name = "".join(re.split("[œÆæŒ]+", song_title))
		file_name = sanitize_filepath(formated_name)
		files = os.listdir(self.folder_path)

		renamed = False

		for file in files:
			if file.startswith(file_name) and file.endswith('.mp3'):
				os.rename(os.path.join(self.folder_path, file), f"{self.folder_path}{song_id}.mp3")
				renamed = True
			if file.startswith(file_name) and file.endswith('.lrc'):
				os.rename(os.path.join(self.folder_path, file), f"{self.folder_path}{song_id}.lrc")
		if not renamed:
			print("Error: failed to rename")

	def __map_tracks(self, tracks):
		result = []
		for track in tracks:
			result.append(track['id'])
		return result

def cli():
	folder_path = "./songs/"

	parser = argparse.ArgumentParser()
	parser.add_argument('-t', help='song title', metavar='title')
	parser.add_argument('-id', help='id of the track', metavar='id')
	parser.add_argument('-arl', help='arl deezer account', metavar='arl')

	args = parser.parse_args()

	if args.arl:
		deezer_dl = DeezerDownloader(args.arl, folder_path)
	else:
		print("Missing Deezer ARL")

	if args.id:
		print("Asked Track ", args.t)
		deezer_dl.dl_track_by_id(args.id)
	elif args.t:
		deezer_dl.dl_track_by_name(args.t.replace("%20", " "))
	else:
		print("Missing Args")
