from abc import abstractmethod

from deezer import Album, Artist, Playlist, Track
from pyramid.connector.deezer.client.a_deezer_client import ADeezerClient
from pyramid.connector.deezer.client.list_paginated import DeezerListPaginated

class IDeezerClientService(ADeezerClient):

	@abstractmethod
	def _search(
		self,
		path: str,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
		**advanced_params: str | int | None,
	) -> DeezerListPaginated:
		pass

	@abstractmethod
	def search(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
		artist: str | None = None,
		album: str | None = None,
		track: str | None = None,
		label: str | None = None,
		dur_min: int | None = None,
		dur_max: int | None = None,
		bpm_min: int | None = None,
		bpm_max: int | None = None,
	) -> DeezerListPaginated:
		pass

	@abstractmethod
	def search_playlists(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Playlist]:
		pass

	@abstractmethod
	def search_albums(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Album]:
		pass

	@abstractmethod
	def search_artists(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Artist]:
		pass

	@abstractmethod
	async def async_get_playlist(self, playlist_id: int) -> Playlist:
		pass

	@abstractmethod
	async def async_get_album(self, album_id: int) -> Album:
		pass

	@abstractmethod
	async def async_get_artist(self, artist_id: int) -> Artist:
		pass

	@abstractmethod
	async def async_get_track(self, track_id: int) -> Track:
		pass
