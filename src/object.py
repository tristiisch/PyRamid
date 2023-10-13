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

class TrackList():
	def __init__(self):
		pass
