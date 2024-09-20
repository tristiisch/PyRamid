

import re
from pyramid.connector.spotify.spotify_type import SpotifyType
from pyramid.data.a_engine_tools import AEngineTools


class SpotifyTools(AEngineTools):

	@classmethod
	def extract_from_url(cls, url) -> tuple[str, SpotifyType | None] | tuple[None, None]:
		# Extract ID and type using regex
		pattern = r"(?<=open\.spotify\.com/)(intl-(?P<intl>\w+)/)?(?P<type>\w+)/(?P<id>\w+)"
		match = re.search(pattern, url)
		if not match:
			return None, None
		type_str = match.group("type").upper()
		if type_str == "PLAYLIST":
			type = SpotifyType.PLAYLIST
		elif type_str == "ARTIST":
			type = SpotifyType.ARTIST
		elif type_str == "ALBUM":
			type = SpotifyType.ALBUM
		elif type_str == "TRACK":
			type = SpotifyType.TRACK
		else:
			type = None

		id = match.group("id")
		return id, type
