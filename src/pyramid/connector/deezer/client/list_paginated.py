from typing import Any, Generic
from urllib.parse import parse_qs, urlparse

from deezer import Resource
from deezer.pagination import ResourceType

from pyramid.connector.deezer.client.a_deezer_client import ADeezerClient


class DeezerListPaginated(Generic[ResourceType]):
	def __init__(
		self,
		client: ADeezerClient,
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

	async def get_all(self) -> list[ResourceType]:
		elements: list[ResourceType] = []

		while self._could_grow():
			elements.extend(await self._async_fetch_next_page())

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
