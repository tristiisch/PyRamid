import os
import unittest
from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.spotify_search import ISpotifySearchService
from pyramid.api.services.tools.tester import ServiceStandalone
from pyramid.services.builder.configuration import ConfigurationBuilder


class SpotifySearchTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)
	
		ServiceStandalone.import_services()
		builder = ConfigurationBuilder()
		builder.general_limit_tracks(100)
		builder.spotify_client_id("9a84b8a2093f4ca9ae0aa1dc2f184b3f")
		builder.spotify_client_secret("4c575d7b7e5e47ee90fcc143672c800b")
		ServiceStandalone.set_service(IConfigurationService, builder.build())
	
		self.spotify_search = ServiceStandalone.get_service(ISpotifySearchService)

	async def test_search_single(self):
		track = await self.spotify_search.search_track("Johnny Hallyday - Allumer le feu")
		self.assertIsNotNone(track)

	async def test_search_multiple(self):
		tracks = await self.spotify_search.search_tracks("Johnny Hallyday")
		self.assertIsNotNone(tracks)

	async def test_search_multiple_limit(self):
		limit = 75
		tracks = await self.spotify_search.search_tracks("Johnny Hallyday", limit)

		size = len(tracks) if tracks is not None else 0
		self.assertEqual(limit, size)

	async def test_search_playlist(self):
		tracks = await self.spotify_search.get_playlist_tracks("Best of Johnny Hallyday - live")
		self.assertIsNotNone(tracks)

	async def test_search_album(self):
		tracks = await self.spotify_search.get_album_tracks("Anthologie Vol. 1")
		self.assertIsNotNone(tracks)

	async def test_search_top(self):
		tracks = await self.spotify_search.get_top_artist("Johnny Hallyday")
		self.assertIsNotNone(tracks)

	async def test_url_artist(self):
		tracks = await self.spotify_search.get_by_url(
			"https://open.spotify.com/intl-fr/artist/2HALYSe657tNJ1iKVXP2xA"
		)
		self.assertIsNotNone(tracks)

	async def test_url_album(self):
		tracks = await self.spotify_search.get_by_url(
			"https://open.spotify.com/album/1mhVZVEHbIYUN7b5DkXF7d"
		)
		self.assertIsNotNone(tracks)

	async def test_url_track(self):
		tracks = await self.spotify_search.get_by_url(
			"https://open.spotify.com/intl-fr/track/1mzZP8UA2RZUXDw33QNmn4"
		)
		self.assertIsNotNone(tracks)

	async def test_url_playlist(self):
		tracks = await self.spotify_search.get_by_url(
			"https://open.spotify.com/playlist/2CEwnRwSNdIvPn7u6E3whG"
		)
		self.assertIsNotNone(tracks)


if __name__ == "__main__":
	unittest.main(failfast=True)
