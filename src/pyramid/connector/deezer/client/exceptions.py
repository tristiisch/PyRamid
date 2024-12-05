
from typing import Any, Self
import aiohttp
from deezer.exceptions import DeezerAPIException, DeezerErrorResponse

class CliDeezerHTTPError(DeezerAPIException):
	"""Specialisation wrapping HTTPError from the requests library."""

	def __init__(self, http_exception: aiohttp.ClientResponseError, *args: object) -> None:
		url = http_exception.request_info.url
		status_code = http_exception.code
		text = http_exception.message
		super().__init__(status_code, url, text, *args)

	@classmethod
	def from_status_code(cls, exc: aiohttp.ClientResponseError) -> DeezerAPIException:
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
	def from_body(cls, json_data: dict[str, Any]) -> DeezerErrorResponse:
		err_json = json_data["error"]
		code = int(err_json["code"])
		if code == 4:
			return CliDeezerRateLimitError(json_data)
		elif code == 800:
			return CliDeezerNoDataException(json_data)
		return cls(json_data)


class CliDeezerRateLimitError(DeezerErrorResponse):
	pass


class CliDeezerNoDataException(DeezerErrorResponse):
	pass
