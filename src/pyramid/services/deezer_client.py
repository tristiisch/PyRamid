from typing import Any

import aiohttp
from deezer import Album, Artist, Client, Playlist, Resource, Track

from pyramid.api.services.deezer_client import IDeezerClientService
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.connector.deezer.client.a_deezer_client import ADeezerClient
from pyramid.connector.deezer.client.exceptions import CliDeezerErrorResponse, CliDeezerHTTPError
from pyramid.connector.deezer.client.list_paginated import DeezerListPaginated
from pyramid.connector.deezer.client.rate_limiter_async import RateLimiterAsync

@pyramid_service(interface=IDeezerClientService)
class DeezerClientService(IDeezerClientService, ADeezerClient, Client, ServiceInjector):

	def __init__(self, app_id=None, app_secret=None, access_token=None, headers=None, **kwargs):
		# super(Client, self).__init__(app_id, app_secret, access_token, headers, **kwargs)

		self.app_id = app_id
		self.app_secret = app_secret
		self.access_token = access_token
		# self.session = requests.Session()

		# headers = headers or {}
		# self.session.headers.update(headers)
		# self.session.close()
		# self.async_session = aiohttp.ClientSession()
		self.rate_limiter = RateLimiterAsync(max_requests=50, time_interval=5)

		def get_paginated_list(
			self,
			relation: str,
			**kwargs,
		) -> DeezerListPaginated:
			return DeezerListPaginated(
				client=self.client,
				base_path=f"{self.type}/{self.id}/{relation}",
				parent=self,
				**kwargs,
			)
		Resource.get_paginated_list = get_paginated_list  # type: ignore

		# def __getattr__(self, item: str) -> Any:
		# 	try:
		# 		return object.__getattribute__(self, item)
		# 	except AttributeError:
		# 		print(f"Attribute '{item}' not found.")
		# Resource.__getattr__ = __getattr__

		def get(self) -> Any:
			raise AttributeError("%s has a missing attribute." % self.__class__.__name__)

		Resource.get = get

	def _search(
		self,
		path: str,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
		**advanced_params: str | int | None,
	) -> DeezerListPaginated:
		return Client._search(self, path, query, strict, ordering, **advanced_params)  # type: ignore

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
		return self._search(
			"",
			query=query,
			strict=strict,
			ordering=ordering,
			artist=artist,
			album=album,
			track=track,
			label=label,
			dur_min=dur_min,
			dur_max=dur_max,
			bpm_min=bpm_min,
			bpm_max=bpm_max,
		)

	def search_playlists(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Playlist]:
		return self._search(
			path="playlist",
			query=query,
			strict=strict,
			ordering=ordering,
		)

	def search_albums(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Album]:
		return self._search(
			path="album",
			query=query,
			strict=strict,
			ordering=ordering,
		)

	def search_artists(
		self,
		query: str = "",
		strict: bool | None = None,
		ordering: str | None = None,
	) -> DeezerListPaginated[Artist]:
		return self._search(
			path="artist",
			query=query,
			strict=strict,
			ordering=ordering,
		)

	async def async_get_playlist(self, playlist_id: int) -> Playlist:
		return await self.async_request("GET", f"playlist/{playlist_id}")  # type: ignore

	async def async_get_album(self, album_id: int) -> Album:
		return await self.async_request("GET", f"album/{album_id}")  # type: ignore

	async def async_get_artist(self, artist_id: int) -> Artist:
		return await self.async_request("GET", f"artist/{artist_id}")  # type: ignore

	async def async_get_track(self, track_id: int) -> Track:
		return await self.async_request("GET", f"track/{track_id}")  # type: ignore

	def _get_paginated_list(self, path, **params) -> DeezerListPaginated:
		return DeezerListPaginated(client=self, base_path=path, **params)

	async def async_request(
		self,
		method: str,
		path: str,
		parent: Resource | None = None,
		resource_type: type[Resource] | None = None,
		resource_id: int | None = None,
		paginate_list=False,
		**params,
	):
		"""
		Make an asynchronous request to the API and parse the response.

		:param method: HTTP verb to use: GET, POST, DELETE, ...
		:param path: The path to make the API call to (e.g. 'artist/1234').
		:param parent: A reference to the parent resource, to avoid fetching again.
		:param resource_type: The resource class to use as the top level.
		:param resource_id: The resource id to use as the top level.
		:param paginate_list: Whether to wrap list into a pagination object.
		:param params: Query parameters to add to the request
		"""

		if self.access_token is not None:
			params["access_token"] = str(self.access_token)

		async with aiohttp.ClientSession() as session:
			await self.rate_limiter.check()
			async with session.request(
				method,
				f"{self.base_url}/{path}",
				params=params,
			) as response:
				await self.rate_limiter.add()
				try:
					response.raise_for_status()
				except aiohttp.ClientResponseError as exc:
					raise CliDeezerHTTPError.from_status_code(exc) from exc

				json_data = await response.json()

		if not isinstance(json_data, dict):
			return json_data

		if "error" in json_data and json_data["error"]:
			raise CliDeezerErrorResponse.from_body(json_data)

		return self._process_json(
			json_data,
			parent=parent,
			resource_type=resource_type,
			resource_id=resource_id,
			paginate_list=paginate_list,
		)
