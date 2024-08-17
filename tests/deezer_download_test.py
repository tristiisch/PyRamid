import os
import shutil
import unittest

from pyramid.connector.deezer.downloader import DeezerDownloader

class DeezerDownloadTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)

		# arl = os.getenv("DEEZER__ARL")
		# if arl is None:
		# 	self.skipTest("Environnement variable DEEZER__ARL is not set.")

		self.path = "./test-songs"
		# self.cli = DeezerDownloader(arl, self.path)
		self.cli = DeezerDownloader(self.path)

	async def test_download(self):
		track = await self.cli.dl_track_by_id(2308590)
		self.assertIsNotNone(track)

	def tearDown(self):
		shutil.rmtree(self.path)


if __name__ == "__main__":
	unittest.main(failfast=True)
