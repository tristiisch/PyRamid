
import re
import aiohttp
from pyramid.data.a_engine_tools import AEngineTools
from pyramid.services.deezer_search import DeezerType


class DeezerTools(AEngineTools):

	@classmethod
	async def extract_from_url(cls, url) -> tuple[int, DeezerType | None] | tuple[None, None]:
		# Resolve if URL is a deezer.page.link URL
		if "deezer.page.link" in url:
			async with aiohttp.ClientSession() as session:
				async with session.get(url, allow_redirects=True) as response:
					url = str(response.url)

		# Extract ID and type using regex
		pattern = r"(?<=deezer.com/fr/)(\w+)/(?P<id>\d+)"
		match = re.search(pattern, url)
		if not match:
			return None, None
		deezer_type_str = match.group(1).upper()
		if deezer_type_str == "PLAYLIST":
			deezer_type = DeezerType.PLAYLIST
		elif deezer_type_str == "ARTIST":
			deezer_type = DeezerType.ARTIST
		elif deezer_type_str == "ALBUM":
			deezer_type = DeezerType.ALBUM
		elif deezer_type_str == "TRACK":
			deezer_type = DeezerType.TRACK
		else:
			deezer_type = None

		deezer_id = int(match.group("id"))
		return deezer_id, deezer_type
