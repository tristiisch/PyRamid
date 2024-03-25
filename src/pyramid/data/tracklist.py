import os
import random

import pyramid.tools.utils as tools
from pyramid.data.track import Track, TrackMinimal, TrackMinimalDeezer


class TrackList:
	def __init__(self):
		self.__tracks: list[Track] = []

	def add_track(self, track: Track) -> bool:
		if not os.path.exists(track.file_local):
			return False
		self.__tracks.append(track)
		return True

	def add_track_after(self, track: Track) -> bool:
		if not os.path.exists(track.file_local):
			return False
		self.__tracks.insert(1, track)
		return True

	def add_tracks(self, tracks: list[Track]):
		self.__tracks.extend(tracks)

	def clear(self) -> bool:
		if self.is_empty():
			return False
		self.__tracks.clear()
		return True

	def shuffle(self, ignore_first=True) -> bool:
		length = len(self.__tracks)
		if length <= 2:
			return False

		if ignore_first:
			first = self.__tracks[0]
			others = self.__tracks[1:]
			random.shuffle(others)
			self.__tracks = [first] + others

		else:
			random.shuffle(self.__tracks)
		return True

	def remove(self, index: int) -> Track | None:
		length = len(self.__tracks)
		if length <= index or index <= 0:
			return None

		track_to_delete = self.__tracks[index]
		del self.__tracks[index]
		return track_to_delete

	def remove_to(self, index: int) -> int:
		length = len(self.__tracks)
		if length <= index or index <= 0:
			return -1
		if index == 1:
			return self.remove(index) is not None

		new_tracks = self.__tracks[:1] + self.__tracks[index:]
		self.__tracks = new_tracks
		return length - len(self.__tracks)

	def is_empty(self) -> bool:
		return len(self.__tracks) == 0

	def has_next(self) -> bool:
		return len(self.__tracks) >= 2

	def first_song(self) -> Track:
		return self.__tracks[0]

	def remove_song(self):
		self.__tracks.pop(0)

	def get_songs_str(self) -> str:
		return to_str(self.__tracks)

	def get_length(self) -> str:
		length = len(self.__tracks)
		if length == 0:
			return f"{length} tracks"
		else:
			return f"{length} track"

	def get_duration(self) -> str:
		return tools.time_to_duration(sum(t.duration_seconds for t in self.__tracks))


def to_str(list_of_track: list[TrackMinimal] | list[TrackMinimalDeezer] | list[Track]) -> str:
	data = [
		[str(i + 1), track.author_name, track.name, track.album_title]
		for i, track in enumerate(list_of_track)
	]
	columns = ["n°", "Author", "Title", "Album"]
	hsa = tools.human_string_array(data, columns, 50)
	return hsa
