from abc import ABC


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
