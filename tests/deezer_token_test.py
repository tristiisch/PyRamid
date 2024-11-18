import os
import unittest

from pyramid.api.services.configuration import IConfigurationService
from pyramid.api.services.deezer_downloader import IDeezerDownloaderService
from pyramid.api.services.tools.tester import ServiceStandalone
from pyramid.data.exceptions import DeezerTokenInvalidException, DeezerTokensUnavailableException
from pyramid.services.builder.configuration import ConfigurationBuilder

class DeezerTokenTest(unittest.IsolatedAsyncioTestCase):
	def __init__(self, methodName: str = "runTest") -> None:
		super().__init__(methodName)

		ServiceStandalone.import_services()
		builder = ConfigurationBuilder().deezer_arl(os.getenv("DEEZER__ARL") or "")
		ServiceStandalone.set_service(IConfigurationService, builder.build())
	
		self.deezer_downloader = ServiceStandalone.get_service(IDeezerDownloaderService)

	async def test_download(self):
		try:
			await self.deezer_downloader.get_client()
		except (DeezerTokenInvalidException, DeezerTokensUnavailableException) as err:
			self.fail(err.msg)


if __name__ == "__main__":
	unittest.main(failfast=True)
