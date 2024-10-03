import unittest
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.api.services.tools.tester import ServiceStandalone

class AlphaService(ServiceInjector):
	def __init__(self):
		self.started = False

	def start(self):
		self.started = True

class BravoService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, alpha_service: AlphaService):
		self.alpha_service = alpha_service

	def start(self):
		self.started = True

class CharlieService(AlphaService):
	pass

class ServiceStandaloneTest(unittest.TestCase):

	def setUp(self):
		ServiceRegister.SERVICES_REGISTRED.clear()
		ServiceRegister.SERVICES_INSTANCES.clear()
		ServiceRegister.ORDERED_SERVICES = None
		ServiceRegister.register_service(AlphaService.__name__, AlphaService)
		ServiceRegister.register_service(BravoService.__name__, BravoService)

	def test_set_service(self):
		ServiceRegister.enable()

		charlie = CharlieService()
		ServiceStandalone.set_service(AlphaService, charlie)

		bravo = ServiceStandalone.get_service(BravoService)
		self.assertEqual(bravo.alpha_service, charlie)

	def test_get_service(self):
		service_instance = AlphaService()
		ServiceStandalone.set_service(AlphaService, service_instance)
		result = ServiceStandalone.get_service(AlphaService)
		self.assertEqual(result, service_instance)

if __name__ == "__main__":
	unittest.main()
