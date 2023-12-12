import abc
import asyncio
import time
from abc import ABC
from typing import Any, Literal, Self
from urllib.parse import parse_qs, urlparse

import aiohttp
from deezer import Client, PaginatedList, Resource
from deezer.exceptions import DeezerAPIException, DeezerErrorResponse
from deezer.pagination import ResourceType


class AsyncRateLimiter:
	def __init__(self, max_requests, time_interval):
		self.max_requests = max_requests
		self.time_interval = time_interval
		self.requests: list[float] = []
		self.lock = asyncio.Lock()

	async def _clean_old_requests(self):
		current_time = time.time()
		self.requests = [t for t in self.requests if self.time_interval > current_time - t]

	async def _wait_if_needed(self):
		async with self.lock:
			await self._clean_old_requests()
			if len(self.requests) >= self.max_requests:
				sleep_time = self.requests[0] + self.time_interval - time.time()
				if sleep_time > 0:
					# logging.warning("Detect Deezer RateLimit - wait %f secs", sleep_time)
					await asyncio.sleep(sleep_time)
					await self._clean_old_requests()

	async def check(self):
		await self._wait_if_needed()

	async def add(self):
		async with self.lock:
			self.requests.append(time.time())


class ACliDeezer(ABC):
	@abc.abstractmethod
	async def async_request(
		self,
		method: str,
		path: str,
		parent: Resource | None = None,
		resource_type: type[Resource] | None = None,
		resource_id: int | None = None,
		paginate_list=False,
		**params,
	) -> Any | list[Any] | dict[str, Any] | Resource | Literal[True]:
		...


class CliPaginatedList(PaginatedList[ResourceType]):
	def __init__(
		self,
		client: ACliDeezer,
		base_path: str,
		parent: Resource | None = None,
		**params,
	):
		self.__client = client
		self.__base_path = base_path
		self.__base_params: dict[str, Any] = params
		self.__next_path: str | None = base_path
		self.__next_params: dict[str, Any] = params
		self.__parent = parent
		self.__total: int | None = None

	async def get_first(self) -> ResourceType | None:
		return await self.get_single(0)

	async def get_single(self, index: int) -> ResourceType | None:
		if 0 > index:
			raise ValueError("index can't be less than 0. (%d received)", index)

		elements = await self._req(False, {"index": index, "limit": 1})

		if index >= len(elements):
			return None

		return elements[0]

	async def get_maximum(self, limit: int):
		if 0 > limit:
			raise ValueError("limit can't be less than 0. (%d received)", limit)
		if limit > 100:
			raise ValueError("You need to use async iterator when limit is bigger than %d", limit)
		elements = await self._req(False, {"limit": limit})

		return elements

	async def get_page(self, item_per_page: int, page: int):
		if 0 > item_per_page:
			raise ValueError("item_per_page can't be less than 0. (%d received)", item_per_page)
		if item_per_page > 100:
			raise NotImplementedError(
				"Pagination with more than 100 items per page is not supported yet."
			)

		index = (page - 1) * item_per_page
		elements = await self._req(False, {"index": index, "limit": item_per_page})
		return elements

	async def total(self) -> int:
		if self.__total is not None:
			return self.__total

		await self._req(False, {"index": 0, "limit": 1})
		assert self.__total is not None
		return self.__total

	def __aiter__(self):
		return self

	async def __anext__(self) -> list[ResourceType]:
		if not self._could_grow():
			raise StopAsyncIteration

		elements = await self._async_fetch_next_page()
		return elements

	def _could_grow(self) -> bool:
		return self.__next_path is not None

	async def _async_fetch_next_page(self) -> list[ResourceType]:
		return await self._req(True)

	async def _req(
		self, use_iterator: bool = False, custom_params: dict[str, Any] | None = None
	) -> list[ResourceType]:
		if use_iterator:
			assert self.__next_path is not None
			path = self.__next_path
			params = self.__next_params
		else:
			path = self.__base_path
			params = self.__base_params

		if custom_params is not None:
			params = params.copy()
			params.update(custom_params)

		response_payload: dict[str, Any] = await self.__client.async_request(
			"GET",
			path,
			parent=self.__parent,
			paginate_list=True,
			resource_type=None,
			resource_id=None,
			**params,
		)  # type: ignore

		if self.__total is None:
			self.__total = response_payload.get("total")

		if use_iterator:
			next_url: str = response_payload.get("next", None)
			if next_url:
				url_bits = urlparse(next_url)
				self.__next_path = url_bits.path.lstrip("/")
				self.__next_params = parse_qs(url_bits.query)
			else:
				self.__next_path = None

		elements: list[ResourceType] = response_payload["data"]

		return elements


class CliDeezer(ACliDeezer, Client):
	def __init__(self, app_id=None, app_secret=None, access_token=None, headers=None, **kwargs):
		super().__init__(app_id, app_secret, access_token, headers, **kwargs)
		# self.async_session = aiohttp.ClientSession()
		self.rate_limiter = AsyncRateLimiter(max_requests=50, time_interval=5)

		def get_paginated_list(
			self,
			relation: str,
			**kwargs,
		) -> CliPaginatedList:
			return CliPaginatedList(
				client=self.client,
				base_path=f"{self.type}/{self.id}/{relation}",
				parent=self,
				**kwargs,
			)
		Resource.get_paginated_list = get_paginated_list

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
	) -> CliPaginatedList:
		return super()._search(
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
		)  # type: ignore

	def _get_paginated_list(self, path, **params) -> CliPaginatedList:
		return CliPaginatedList(client=self, base_path=path, **params)

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


class CliDeezerHTTPError(DeezerAPIException):
	"""Specialisation wrapping HTTPError from the requests library."""

	def __init__(self, http_exception: aiohttp.ClientResponseError, *args: object) -> None:
		url = http_exception.request_info.url
		status_code = http_exception.code
		text = http_exception.message
		super().__init__(status_code, url, text, *args)

	@classmethod
	def from_status_code(cls, exc: aiohttp.ClientResponseError) -> Self:
		"""Initialise the appropriate internal exception from a HTTPError."""
		if exc.code in {502, 503, 504}:
			return CliDeezerRetryableHTTPError(exc)
		if exc.code == 403:
			return CliDeezerForbiddenError(exc)
		if exc.code == 404:
			return CliDeezerNotFoundError(exc)
		return cls(exc)


class CliDeezerRetryableException(DeezerAPIException):
	"""A request failing with this might work if retried."""


class CliDeezerRetryableHTTPError(CliDeezerRetryableException, CliDeezerHTTPError):
	"""A HTTP error due to a potentially temporary issue."""


class CliDeezerForbiddenError(CliDeezerHTTPError):
	"""A HTTP error cause by permission denied error."""


class CliDeezerNotFoundError(CliDeezerHTTPError):
	"""For 404 HTTP errors."""


class CliDeezerErrorResponse(DeezerErrorResponse):
	@classmethod
	def from_body(cls, json_data: dict[str, Any]) -> Self:
		err_json = json_data["error"]
		i = err_json["code"]
		if int(i) == 4:
			return CliDeezerRateLimitError(json_data)
		return cls(json_data)


class CliDeezerRateLimitError(CliDeezerErrorResponse):
	pass
