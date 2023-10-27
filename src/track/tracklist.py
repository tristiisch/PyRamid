import os
import random
import tools.format_list
import tools.utils

from track.track import Track


class TrackList:
	def __init__(self):
		self.__tracks: list[Track] = []

	def add_song(self, track: Track) -> bool:
		if not os.path.exists(track.file_local):
			return False
		self.__tracks.append(track)
		return True

	def add_songs(self, tracks: list[Track]):
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

	def is_empty(self) -> bool:
		return len(self.__tracks) == 0

	def has_next(self) -> bool:
		return len(self.__tracks) >= 2

	def first_song(self) -> Track:
		return self.__tracks[0]

	def remove_song(self):
		self.__tracks.pop(0)

	def get_songs_str(self) -> str:
		return tools.format_list.tracks(self.__tracks)

	def get_length(self) -> str:
		length = len(self.__tracks)
		if length == 0:
			return f"{length} tracks"
		else:
			return f"{length} track"

	def get_duration(self) -> str:
		return tools.utils.time_to_duration(sum(t.duration_seconds for t in self.__tracks))
