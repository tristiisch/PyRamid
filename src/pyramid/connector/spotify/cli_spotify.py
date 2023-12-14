import json
import logging
from venv import logger

import aiohttp
from spotipy import Spotify
from spotipy.exceptions import SpotifyException


class CliSpotify(Spotify):
	async def async_search(self, q, limit=10, offset=0, type="track", market=None):
		return await self._get_async(
			"search", q=q, limit=limit, offset=offset, type=type, market=market
		)

	async def async_track(self, track_id, market=None):
		trid = self._get_id("track", track_id)
		return await self._get_async("tracks/" + trid, market=market)

	async def async_playlist_items(
		self,
		playlist_id,
		fields=None,
		limit=100,
		offset=0,
		market=None,
		additional_types=("track", "episode"),
	):
		plid = self._get_id("playlist", playlist_id)
		return await self._get_async(
			"playlists/%s/tracks" % (plid),
			limit=limit,
			offset=offset,
			fields=fields,
			market=market,
			additional_types=",".join(additional_types),
		)

	async def async_album_tracks(self, album_id, limit=50, offset=0, market=None):
		trid = self._get_id("album", album_id)
		return await self._get_async(
			"albums/" + trid + "/tracks/", limit=limit, offset=offset, market=market
		)

	async def async_artist_top_tracks(self, artist_id, country="US"):
		trid = self._get_id("artist", artist_id)
		return await self._get_async("artists/" + trid + "/top-tracks", country=country)

	async def async_next(self, result):
		if result["next"]:
			return await self._get_async(result["next"])
		else:
			return None

	async def _get_async(self, url, args=None, payload=None, **kwargs):
		if args:
			kwargs.update(args)

		return await self._async_internal_call("GET", url, payload, kwargs)

	async def _async_internal_call(self, method, url, payload, params):
		args = dict(params=params)
		if not url.startswith("http"):
			url = self.prefix + url
		headers = self._auth_headers()

		if "content_type" in args["params"]:
			headers["Content-Type"] = args["params"]["content_type"]
			del args["params"]["content_type"]
			if payload:
				args["data"] = payload
		else:
			headers["Content-Type"] = "application/json"
			if payload:
				args["data"] = json.dumps(payload)

		if self.language is not None:
			headers["Accept-Language"] = self.language

		params = (
			{key: value for key, value in args["params"].items() if value is not None}
			if "params" in args
			else dict()
		)
		logging.debug(
			"Sending %s to %s with Params: %s Headers: %s and Body: %r ",
			method,
			url,
			params,
			headers,
			args.get("data"),
		)
		async with aiohttp.ClientSession() as session:
			async with session.request(
				method,
				url,
				headers=headers,
				proxy=self.proxies,
				timeout=self.requests_timeout,
				params=params,
			) as response:
				try:
					response.raise_for_status()
					results = await response.json()
				except aiohttp.ClientResponseError:
					try:
						json_response = await response.json()
						error = json_response.get("error", {})
						msg = error.get("message")
						reason = error.get("reason")
					except json.JSONDecodeError:
						msg = await response.text() or None
						reason = None

					logger.error(
						"HTTP Error for %s to %s with Params: %s returned %s due to %s",
						method,
						url,
						args.get("params"),
						response.status,
						msg,
					)
					raise SpotifyException(
						response.status,
						-1,
						"%s:\n %s" % (response.url, msg),
						reason=reason,
						headers=response.headers,
					)

		logger.debug("RESULTS: %s", results)
		return results
