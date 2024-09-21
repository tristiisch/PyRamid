from datetime import datetime

from pyramid.data.music.track_minimal import TrackMinimal
from pyramid.tools import utils

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
