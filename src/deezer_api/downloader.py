import argparse
from asyncio import to_thread
import asyncio
import os
import re
import pydeezer.util

from pydeezer import Deezer
from pydeezer.constants import track_formats
from pathvalidate import sanitize_filepath
from tools.object import *

class DeezerDownloader:
	def __init__(self, arl, folder):
		self.deezer_api = Deezer(arl)
		self.folder_path = folder
		self.music_format = track_formats.MP3_128

	def get_track_by_name(self, name) -> TrackMinimal | None:
		tracks_found = self.deezer_api.search_tracks(name)
		if not tracks_found:
			return None
		track = TrackMinimal(tracks_found[0])
		return track

	async def dl_track_by_id(self, track_id) -> Track | None:
		track_to_dl = self.deezer_api.get_track(track_id)
		if not track_to_dl:
			return None

		track_info = track_to_dl['info']
		file_name = pydeezer.util.clean_filename(f"{track_info['DATA']['ART_NAME']} - {track_info['DATA']['SNG_TITLE']}")
		file_path = os.path.join(self.folder_path, file_name) + ".mp3"

		if os.path.exists(file_path) == False:
			await asyncio.get_event_loop().run_in_executor(None,
				self.deezer_api.download_track, track_info, self.folder_path, self.music_format, True, file_name, False, True, False)
			# track_to_dl['download'](self.folder_path, filename = file_name, quality = self.music_format, with_lyrics = False)
			# self.deezer_api.download_track(track_info, self.folder_path, filename = file_name, quality = self.music_format, with_lyrics = False)

		track_downloaded = Track(track_info['DATA'], file_path)
		return track_downloaded

	async def dl_track_by_name(self, name) -> Track | None:
		track : TrackMinimal | None = self.get_track_by_name(name)
		if track == None:
			return None

		track_downloaded = await self.dl_track_by_id(track.id)
		return track_downloaded

	async def test(self, name) -> list[Track] | None:
		tracks_found = self.deezer_api.search_tracks(name)
		if not tracks_found:
			return None
		tracks = [TrackMinimal(item) for item in tracks_found[:10]]
		tracks_dl = [await self.dl_track_by_id(item.id) for item in tracks]
		tracks_dl_filtered = [track for track in tracks_dl if track is not None]  # Filter out None values
		return tracks_dl_filtered

async def cli():
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
		exit(1)

	if args.id:
		print("Asked Track ", args.t)
		await deezer_dl.dl_track_by_id(args.id)
	elif args.t:
		await deezer_dl.dl_track_by_name(args.t.replace("%20", " "))
	else:
		print("Missing Args")
