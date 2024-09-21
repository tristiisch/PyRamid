
import deezer

from pyramid.data.music.track_minimal import TrackMinimal

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
