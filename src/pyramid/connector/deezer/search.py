import asyncio
import logging
import re
from enum import Enum
import aiohttp

import deezer
from pyramid.data.a_engine_tools import AEngineTools
from pyramid.data.a_search import ASearch, ASearchId
from pyramid.data.track import TrackMinimalDeezer

from pyramid.connector.deezer.cli_deezer import (
	CliDeezer,
	CliDeezerNoDataException,
	CliDeezerRateLimitError,
	CliPaginatedList,
)


class DeezerSearch(ASearchId, ASearch):
	def __init__(self, default_limit: int):
		self.default_limit = default_limit
		self.client = CliDeezer()
		self.tools = DeezerTools()
		self.strict = False

	async def search_track(self, search) -> TrackMinimalDeezer | None:
		result = self.client.search(query=search)
		track = await result.get_first()
		if not track:
			return None
		return TrackMinimalDeezer(track)

	async def get_track_by_id(self, track_id: int) -> TrackMinimalDeezer | None:
		track = await self.client.async_get_track(track_id)  # TODO handle HTTP errors
		if not track:
			return None
		return TrackMinimalDeezer(track)

	async def get_track_by_isrc(self, isrc: str) -> TrackMinimalDeezer | None:
		try:
			track: deezer.Track = await self.client.async_request("GET", f"track/isrc:{isrc}")  # type: ignore
			if not track:
				return None
			return TrackMinimalDeezer(track)
		except CliDeezerNoDataException:
			return None

	async def search_tracks(
		self, search, limit: int | None = None
	) -> list[TrackMinimalDeezer] | None:
		if limit is None:
			limit = self.default_limit

		pagination_results = self.client.search(query=search, strict=self.strict)
		tracks = await pagination_results.get_maximum(limit)
		if not tracks:
			return None

		return [TrackMinimalDeezer(element) for element in tracks]

	async def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalDeezer] | None:
		pagination_results = self.client.search_playlists(query=playlist_name, strict=self.strict)
		playlist = await pagination_results.get_first()
		if not playlist:
			return None
		pagination_tracks: CliPaginatedList[deezer.Track] = playlist.get_tracks()  # type: ignore
		tracks = await pagination_tracks.get_all()
		return [TrackMinimalDeezer(element) for element in tracks]

	async def get_playlist_tracks_by_id(
		self, playlist_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		playlist = await self.client.async_get_playlist(playlist_id)  # TODO handle HTTP errors
		if not playlist:
			return None
		# Tracks id are the not the good one
		playlist_tracks: CliPaginatedList[deezer.Track] = playlist.get_tracks()  # type: ignore

		# So we search the id for same name and artist
		real_tracks: list[TrackMinimalDeezer] = []
		unfindable_track: list[TrackMinimalDeezer] = []

		async for chunk_tracks in playlist_tracks:
			for t in chunk_tracks:
				track = await self.search_exact_track(t.artist.name, t.album.title, t.title)
				# logging.info("DEBUG song '%s' - '%s' - '%s'", t.artist.name, t.title, t.album.title)
				if track is None:
					if not t.readable:
						logging.warning(
							"Unavailable track in playlist '%s' - '%s'", t.artist.name, t.title
						)
					else:
						logging.warning(
							"Unknown track searched in playlist '%s' - '%s'", t.artist.name, t.title
						)
					unfindable_track.append(TrackMinimalDeezer(t))
					continue
				real_tracks.append(track)

		return real_tracks, unfindable_track

	async def get_album_tracks(self, album_name) -> list[TrackMinimalDeezer] | None:
		pagination_results = self.client.search_albums(query=album_name, strict=self.strict)
		album = await pagination_results.get_first()
		if not album:
			return None
		pagination_tracks: CliPaginatedList[deezer.Track] = album.get_tracks()  # type: ignore
		tracks = await pagination_tracks.get_all()
		return [TrackMinimalDeezer(element) for element in tracks]

	async def get_album_tracks_by_id(
		self, album_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		album = await self.client.async_get_album(album_id)  # TODO handle HTTP errors
		if not album:
			return None
		pagination_tracks: CliPaginatedList[deezer.Track] = album.get_tracks()  # type: ignore
		tracks = await pagination_tracks.get_all()
		return [TrackMinimalDeezer(element) for element in tracks], []

	async def get_top_artist(
		self, artist_name, limit: int | None = None
	) -> list[TrackMinimalDeezer] | None:
		if limit is None:
			limit = self.default_limit
		pagination_results = self.client.search_artists(query=artist_name, strict=self.strict)
		artist = await pagination_results.get_first()
		if not artist:
			return None
		pagination_tracks: CliPaginatedList[deezer.Track] = artist.get_top()  # type: ignore
		tracks = await pagination_tracks.get_maximum(limit)
		return [TrackMinimalDeezer(element) for element in tracks]

	async def get_top_artist_by_id(
		self, artist_id: int, limit: int | None = None
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		if limit is None:
			limit = self.default_limit
		artist = await self.client.async_get_artist(artist_id)  # TODO handle HTTP errors
		if not artist:
			return None
		pagination_tracks: CliPaginatedList[deezer.Track] = artist.get_top()  # type: ignore
		tracks = await pagination_tracks.get_maximum(limit)
		return [TrackMinimalDeezer(element) for element in tracks], []

	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | TrackMinimalDeezer | None:
		id, type = await self.tools.extract_from_url(url)

		if id is None:
			return None
		if type is None:
			raise NotImplementedError(f"The type of deezer info '{url}' is not implemented")

		tracks: (
			tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | TrackMinimalDeezer | None
		)

		if type == DeezerType.PLAYLIST:
			# future = asyncio.get_event_loop().run_in_executor(
			# 	None, self.get_playlist_tracks_by_id, id
			# )
			# tracks = await asyncio.wrap_future(future)
			tracks = await self.get_playlist_tracks_by_id(id)
		elif type == DeezerType.ARTIST:
			tracks = await self.get_top_artist_by_id(id)
		elif type == DeezerType.ALBUM:
			tracks = await self.get_album_tracks_by_id(id)
		elif type == DeezerType.TRACK:
			tracks = await self.get_track_by_id(id)
		else:
			raise NotImplementedError(f"The type of deezer info '{type}' can't be resolve")

		return tracks

	async def search_exact_track(
		self, artist_name, album_title, track_title
	) -> TrackMinimalDeezer | None:
		clean_artist = self.__remove_special_chars(artist_name)
		clean_album = self.__remove_special_chars(album_title)
		clean_track = self.__remove_special_chars(track_title)
		# logging.info("Song CLEANED '%s' - '%s' - '%s'", clean_artist, clean_track, clean_album)

		track = await self._search_exact_track(clean_artist, clean_album, clean_track)
		if track is None:
			track = await self._search_exact_track(clean_artist, None, clean_track)
			if track is None:
				track = await self._search_exact_track(None, clean_album, clean_track)
				if track is None:
					track = await self._search_exact_track(None, None, clean_track)
					# if track is not None:
					# logging.warning("Find with title '%s' - '%s' - '%s'", clean_artist, clean_track, clean_album)
				# else:
				# logging.warning("Find with album & title '%s' - '%s' - '%s'", clean_artist, clean_track, clean_album)
			# else:
			# logging.warning("Find with artist & title '%s' - '%s' - '%s'", clean_artist, clean_track, clean_album)
		return track

	async def _search_exact_track(
		self, artist_name, album_title, track_title
	) -> TrackMinimalDeezer | None:
		try:
			pagination_results = self.client.search(
				artist=artist_name, album=album_title, track=track_title
			)
			logging.info("_search_exact_track %s - %s - %s", artist_name, album_title, track_title)
			track = await pagination_results.get_first()
			if track is None:
				return None
			return TrackMinimalDeezer(track)

		except CliDeezerRateLimitError:
			logging.error("Search Deezer RateLimit %s - %s", artist_name, track_title)
			await asyncio.sleep(5)
			return await self._search_exact_track(artist_name, album_title, track_title)

	def __remove_special_chars(
		self, input_string: str | None, allowed_brackets: tuple = ("(", ")", "[", "]")
	):
		if input_string is None or input_string == "":
			return None

		open_brackets = [b for i, b in enumerate(allowed_brackets) if i % 2 == 0]
		close_brackets = [b for i, b in enumerate(allowed_brackets) if i % 2 != 0]
		stack: list[str] = []
		result: list[str] = []
		last_char: str | None = None  # Keep track of the last processed character

		for char in input_string:
			if char in open_brackets:
				stack.append(char)
			elif char in close_brackets:
				if stack:
					open_bracket = stack.pop()
					if open_brackets.index(open_bracket) == close_brackets.index(char):
						continue
				if last_char != " ":  # Append only if the previous character is not a space
					result.append(char)
			elif char.isspace():
				if last_char != " ":  # Append only if the previous character is not a space
					result.append(char)
			# elif not stack and (char.isalnum() or char == "'" or char == "/"):
			elif not stack:
				result.append(char)
			else:
				continue
			last_char = char  # Update last_char

		return "".join(result)


class DeezerType(Enum):
	PLAYLIST = 1
	ARTIST = 2
	ALBUM = 3
	TRACK = 4


class DeezerTools(AEngineTools):
	async def extract_from_url(self, url) -> tuple[int, DeezerType | None] | tuple[None, None]:
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
