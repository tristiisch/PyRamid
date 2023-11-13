import asyncio
import logging
import re
import time
from enum import Enum
from typing import List
import requests

import deezer
from deezer import Client, PaginatedList
from deezer.client import DeezerErrorResponse

from data.track import TrackMinimalDeezer
from data.a_search import ASearch, ASearchId
from data.a_engine_tools import AEngineTools


class DeezerSearch(ASearchId, ASearch):
	def __init__(self, default_limit: int):
		self.default_limit = default_limit
		self.client = Client()
		self.tools = DeezerTools()
		self.strict = False

	def search_track(self, search) -> TrackMinimalDeezer | None:
		search_results = self.client.search(query=search)
		if not search_results or len(search_results) == 0:
			return None
		track = search_results[0]
		return TrackMinimalDeezer(track)

	def get_track_by_id(self, track_id: int) -> TrackMinimalDeezer | None:
		track = self.client.get_track(track_id)  # TODO handle HTTP errors
		if not track:
			return None
		return TrackMinimalDeezer(track)

	def search_tracks(self, search, limit: int | None = None) -> list[TrackMinimalDeezer] | None:
		if limit is None:
			limit = self.default_limit

		search_results = self.client.search(query=search, strict=self.strict)

		if not search_results or len(search_results) == 0:
			return None
		tracks = search_results[:limit]
		return [TrackMinimalDeezer(element) for element in tracks]

	def get_playlist_tracks(self, playlist_name) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search_playlists(query=playlist_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		playlist = search_results[0]
		return [TrackMinimalDeezer(element) for element in playlist.get_tracks()]

	def get_playlist_tracks_by_id(
		self, playlist_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		playlist = self.client.get_playlist(playlist_id)  # TODO handle HTTP errors
		if not playlist:
			return None
		# Tracks id are the not the good one
		playlist_tracks: PaginatedList[deezer.Track] = playlist.get_tracks()

		# So we search the id for same name and artist
		real_tracks: list[TrackMinimalDeezer] = [] * len(playlist_tracks)
		unfindable_track: list[TrackMinimalDeezer] = []

		while playlist_tracks._could_grow():
			chunk_tracks = playlist_tracks._fetch_next_page()
			rt, ut = self.__iter_playlist(chunk_tracks)
			real_tracks.extend(rt)
			unfindable_track.extend(ut)

		return real_tracks, unfindable_track

	def __iter_playlist(self, playlist_tracks: List[deezer.Track]):
		real_tracks: list[TrackMinimalDeezer] = []
		unfindable_track: list[TrackMinimalDeezer] = []

		for t in playlist_tracks:
			track = self.search_exact_track(t.artist.name, None, t.title)
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

	def get_album_tracks(self, album_name) -> list[TrackMinimalDeezer] | None:
		search_results = self.client.search_albums(query=album_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		album = search_results[0]
		return [TrackMinimalDeezer(element) for element in album.get_tracks()]

	def get_album_tracks_by_id(
		self, album_id: int
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		album = self.client.get_album(album_id)  # TODO handle HTTP errors
		if not album:
			return None
		return [TrackMinimalDeezer(element) for element in album.get_tracks()], []

	def get_top_artist(self, artist_name, limit: int | None = None) -> list[TrackMinimalDeezer] | None:
		if limit is None:
			limit = self.default_limit
		search_results = self.client.search_artists(query=artist_name, strict=self.strict)
		if not search_results or len(search_results) == 0:
			return None
		artist = search_results[0]
		top_tracks = artist.get_top()[:limit]
		return [TrackMinimalDeezer(element) for element in top_tracks]

	def get_top_artist_by_id(
		self, artist_id: int, limit: int | None = None
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | None:
		if limit is None:
			limit = self.default_limit
		artist = self.client.get_artist(artist_id)  # TODO handle HTTP errors
		if not artist:
			return None
		top_tracks = artist.get_top()[:limit]
		return [TrackMinimalDeezer(element) for element in top_tracks], []

	async def get_by_url(
		self, url
	) -> tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | TrackMinimalDeezer | None:
		id, type = self.tools.extract_from_url(url)

		if id is None:
			return None
		if type is None:
			raise NotImplementedError(f"The type of deezer info '{url}' is not implemented")

		tracks: (
			tuple[list[TrackMinimalDeezer], list[TrackMinimalDeezer]] | TrackMinimalDeezer | None
		)

		if type == DeezerType.PLAYLIST:
			future = asyncio.get_event_loop().run_in_executor(
				None, self.get_playlist_tracks_by_id, id
			)
			tracks = await asyncio.wrap_future(future)
		elif type == DeezerType.ARTIST:
			tracks = self.get_top_artist_by_id(id)
		elif type == DeezerType.ALBUM:
			tracks = self.get_album_tracks_by_id(id)
		elif type == DeezerType.TRACK:
			tracks = self.get_track_by_id(id)
		else:
			raise NotImplementedError(f"The type of deezer info '{type}' can't be resolve")

		return tracks

	def search_exact_track(
		self, artist_name, album_title, track_title
	) -> TrackMinimalDeezer | None:
		clean_artist = self.__remove_special_chars(artist_name)
		clean_album = self.__remove_special_chars(album_title)
		clean_track = self.__remove_special_chars(track_title)
		# logging.info("Song CLEANED '%s' - '%s' - '%s'", clean_artist, clean_track, clean_album)

		try:
			search_results = self.client.search(
				artist=clean_artist, album=clean_album, track=clean_track
			)
			if not search_results:
				return None
			track = search_results[0]  # TODO Check if the first one is the most appropriate
			return TrackMinimalDeezer(track)

		except DeezerErrorResponse as err:
			err_json = err.json_data["error"]
			i = err_json["code"]  # type: ignore
			if int(i) == 4:
				time.sleep(5)
				logging.warning("Search RateLimit %s - %s", artist_name, track_title)
				return self.search_exact_track(artist_name, album_title, track_title)
			else:
				raise err

	def __remove_special_chars(
		self, input_string: str | None, allowed_brackets: tuple = ("(", ")", "[", "]")
	):
		if input_string is None:
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
	def extract_from_url(self, url) -> tuple[int, DeezerType | None] | tuple[None, None]:
		# Resolve if URL is a deezer.page.link URL
		if "deezer.page.link" in url:
			response = requests.get(url, allow_redirects=True)
			url = response.url

		# Extract ID and type using regex
		pattern = r"(?<=deezer.com/fr/)(\w+)/(?P<id>\d+)"
		match = re.search(pattern, url)
		if match:
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
		else:
			return None, None
