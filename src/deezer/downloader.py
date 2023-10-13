import argparse
import os
import re

from pydeezer import Deezer
from pydeezer.constants import track_formats
from pathvalidate import sanitize_filepath
from object import *

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
