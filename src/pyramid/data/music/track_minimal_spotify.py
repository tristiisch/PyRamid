

from pyramid.data.music.track_minimal import TrackMinimal


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
