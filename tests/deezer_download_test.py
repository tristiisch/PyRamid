import os
import shutil
import unittest

from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.deezer_downloader import IDeezerDownloaderService
from pyramid.api.services.tools.tester import ServiceStandalone
from pyramid.services.builder.configuration import ConfigurationBuilder

class DeezerDownloadTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)

		self.path = "./tests-songs"
		os.makedirs(self.path, exist_ok=True)

		ServiceStandalone.import_services()
		builder = ConfigurationBuilder().deezer_folder(self.path).deezer_arl(os.getenv("DEEZER__ARL") or "")
		ServiceStandalone.set_service(IConfigurationService, builder.build())
	
		self.deezer_downloader = ServiceStandalone.get_service(IDeezerDownloaderService)

	async def test_download(self):
		track = await self.deezer_downloader.dl_track_by_id(2308590)
		self.assertIsNotNone(track)

	def tearDown(self):
		shutil.rmtree(self.path)


if __name__ == "__main__":
	unittest.main(failfast=True)
