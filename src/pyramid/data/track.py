from abc import ABC
from datetime import datetime

import deezer
from pyramid.tools import utils


class TrackMinimal(ABC):
	def __init__(self, data):
		self.id: str
		self.author_name: str
		self.author_picture: str
		self.name: str
		self.album_title: str
		self.album_picture: str
		self.available = True

	def get_full_name(self) -> str:
		return f"{self.author_name} - {self.name}"

	def format_duration(self, input: int) -> str:
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

	def __str__(self):
		return f"{self.author_name} - {self.name} - {self.album_title}"


class TrackMinimalSpotify(TrackMinimal):
	def __init__(self, data):
		# author_picture = data['artists'][0]['images'][0]['url'] if data['artists'][0]['images'] else ""
		# author_picture : str = "" # TODO Fix it
		album_picture = data["album"]["images"][0]["url"] if data["album"]["images"] else ""
		self.id: str = data["id"]
		self.author_name: str = data["artists"][0]["name"]
		self.author_picture: str = ""
		self.name: str = data["name"]
		self.album_title: str = data["album"]["name"]
		self.album_picture: str = album_picture
		self.disk_number: int = data["disc_number"]
		self.track_number: int = data["track_number"]
		self.explicit: bool = data["explicit"]
		self.duration: int = round(data["duration_ms"] / 1000)
		self.isrc: str | None = (
			data["external_ids"]["isrc"] if "isrc" in data["external_ids"] else None
		)
		# self.available_countries: list[str] = data["available_markets"]
		self.available = not data["is_local"]


class TrackMinimalDeezer(TrackMinimal):
	def __init__(self, data: deezer.Track):
		self.id: str = str(data.id)
		self.author_name: str = data.artist.name
		# self.author_picture: str = data.artist.picture_medium
		self.name: str = data.title
		self.album_title: str = data.album.title
		self.album_picture: str = data.album.cover_xl
		# self.disk_number: int = data.disk_number
		# self.track_number: int = data.track_position
		self.explicit: bool = data.explicit_lyrics
		self.duration: int = data.duration
		self.rank: int = data.rank
		# self.isrc: str = data.isrc
		# self.available_countries: list[str] = data.available_countries
		if not data.readable:
			# logging.warning("%s - %s is unreadable", self.author_name, self.name)
			self.available = False
		else:
			self.available = True


class Track(TrackMinimal):
	def __init__(self, data, file_path):
		self.author_name: str = data["ART_NAME"]
		self.author_picture: str = f"https://e-cdn-images.dzcdn.net/images/artist/{data['ART_PICTURE']}/512x512-000000-80-0-0.jpg"
		self.authors: list[str] = [element["ART_NAME"] for element in data["ARTISTS"]]
		self.name: str = data["SNG_TITLE"]
		self.album_title: str = data["ALB_TITLE"]
		self.album_picture: str = f"https://e-cdn-images.dzcdn.net/images/cover/{data['ALB_PICTURE']}/1024x1024-000000-80-0-0.jpg"
		self.actual_seconds: int = int(0)
		self.duration_seconds: int = int(data["DURATION"])
		self.duration: str = self.format_duration(int(data["DURATION"]))
		self.file_size: int = int(data["FILESIZE"])
		if self.__is_valid_date(data["PHYSICAL_RELEASE_DATE"]):
			self.date = datetime.strptime(data["PHYSICAL_RELEASE_DATE"], "%Y-%m-%d")
		else:
			self.date = None
		self.file_local: str = file_path

	def get_date(self, locale: str = "en-US") -> str | None:
		if self.date is None:
			return None
		date_formatted = utils.format_date_by_country(self.date, locale)
		return date_formatted

	def __is_valid_date(self, date: str):
		# Check if the format is exactly "YYYY-MM-DD"
		parts = date.split("-")
		if len(parts) == 3 and len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
			year, month, day = parts
			if year.isdigit() and month.isdigit() and day.isdigit():
				if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
					return True
		return False
