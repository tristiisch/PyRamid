import os
import unittest

from pyramid.connector.deezer.downloader import DeezerDownloader
from pyramid.connector.deezer.search import DeezerSearch

class DeezerSearchTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)

		limit = int(os.getenv("GENERAL__LIMIT_TRACKS", 100))
		self.cli = DeezerSearch(limit)

	async def test_search_single(self):
		track = await self.cli.search_track("Johnny Hallyday - Allumer le feu")
		self.assertIsNotNone(track)

	async def test_search_multiple(self):
		tracks = await self.cli.search_tracks("Johnny Hallyday")
		self.assertIsNotNone(tracks)

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
		tracks = await self.cli.get_by_url("https://www.deezer.com/fr/artist/1060")
		self.assertIsNotNone(tracks)

	# async def test_url_artist_2nd_format(self):
	# 	tracks = await self.cli.get_by_url("https://deezer.page.link/HWapYqfpsmSukE6T7")
	# 	self.assertIsNotNone(tracks)

	async def test_url_album(self):
		tracks = await self.cli.get_by_url("https://www.deezer.com/fr/album/53012892")
		self.assertIsNotNone(tracks)

	# async def test_url_album_2nd_format(self):
	# 	tracks = await self.cli.get_by_url("https://deezer.page.link/gvryHN1VUn62CnCJ7")
	# 	self.assertIsNotNone(tracks)

	async def test_url_track(self):
		tracks = await self.cli.get_by_url("https://www.deezer.com/fr/track/2308590")
		self.assertIsNotNone(tracks)

	# async def test_url_track_2nd_format(self):
	# 	tracks = await self.cli.get_by_url("https://deezer.page.link/qF6ucYP2wSGsLiMB6")
	# 	self.assertIsNotNone(tracks)

	async def test_url_playlist(self):
		tracks = await self.cli.get_by_url("https://www.deezer.com/fr/playlist/987181371")
		self.assertIsNotNone(tracks)

	# async def test_url_playlist_2nd_format(self):
	# 	tracks = await self.cli.get_by_url("https://deezer.page.link/ibwojNjEKAQjsKgZ9")
	# 	self.assertIsNotNone(tracks)

if __name__ == "__main__":
	unittest.main(failfast=True)
