import os
import unittest
from pyramid.connector.spotify.search import SpotifySearch


class SpotifySearchTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)

		limit = int(os.getenv("GENERAL__LIMIT_TRACKS", 100))
		client_id = os.getenv("SPOTIFY__CLIENT_ID", "c760faf4271a4e30b0f5a1a228b0a8d6")
		client_secret = os.getenv("SPOTIFY__CLIENT_SECRET", "a122b8f9fb5741b99e5ce88805bebe35")
		self.cli = SpotifySearch(limit, client_id, client_secret)

	async def test_search_single(self):
		track = await self.cli.search_track("Johnny Hallyday - Allumer le feu")
		self.assertIsNotNone(track)

	async def test_search_multiple(self):
		tracks = await self.cli.search_tracks("Johnny Hallyday")
		self.assertIsNotNone(tracks)

	async def test_search_multiple_limit(self):
		limit = 75
		tracks = await self.cli.search_tracks("Johnny Hallyday", limit)

		size = len(tracks) if tracks is not None else 0
		self.assertEqual(limit, size)

	async def test_search_playlist(self):
		tracks = await self.cli.get_playlist_tracks("Best of Johnny Hallyday - live")
		self.assertIsNotNone(tracks)

	async def test_search_album(self):
		tracks = await self.cli.get_album_tracks("Anthologie Vol. 1")
		self.assertIsNotNone(tracks)

	async def test_search_top(self):
		tracks = await self.cli.get_top_artist("Johnny Hallyday")
		self.assertIsNotNone(tracks)

	async def test_url_artist(self):
		tracks = await self.cli.get_by_url(
			"https://open.spotify.com/intl-fr/artist/2HALYSe657tNJ1iKVXP2xA?si=e5x_arTGSqWtnRrJjCCTdQ"
		)
		self.assertIsNotNone(tracks)

	async def test_url_album(self):
		tracks = await self.cli.get_by_url(
			"https://open.spotify.com/album/1mhVZVEHbIYUN7b5DkXF7d?si=U9HaPDJtRdSnT9qZaQxjXA"
		)
		self.assertIsNotNone(tracks)

	async def test_url_track(self):
		tracks = await self.cli.get_by_url(
			"https://open.spotify.com/intl-fr/track/1mzZP8UA2RZUXDw33QNmn4?si=4c27f893cd7c4055"
		)
		self.assertIsNotNone(tracks)

	async def test_url_playlist(self):
		tracks = await self.cli.get_by_url(
			"https://open.spotify.com/playlist/37i9dQZF1DZ06evO1ymAtQ?si=5c4b6ff36a0d4c98"
		)
		self.assertIsNotNone(tracks)


if __name__ == "__main__":
	unittest.main(failfast=True)
