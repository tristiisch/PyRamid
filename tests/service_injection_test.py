import unittest
from unittest.mock import patch, Mock
from pyramid.api.services.tools.exceptions import ServiceCicularDependencyException, ServiceNotRegisteredException
from pyramid.api.services.tools.register import ServiceRegister
from pyramid.api.services.tools.injector import ServiceInjector

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

class CharlieService(ServiceInjector):
	def __init__(self):
		self.started = False

	def start(self):
		self.started = True

class DeltaService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, alpha_service: AlphaService, bravo_service: BravoService, foxtrot_service: 'FoxtrotService'):
		self.alpha_service = alpha_service
		self.bravo_service = bravo_service
		self.foxtrot_service = foxtrot_service

	def start(self):
		self.started = True

class EchoService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, alpha_service: AlphaService, charlie_service: CharlieService):
		self.alpha_service = alpha_service
		self.charlie_service = charlie_service

	def start(self):
		self.started = True

class FoxtrotService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, echo_service: EchoService):
		self.echo_service = echo_service

	def start(self):
		self.started = True

class GolfService(ServiceInjector):
	def __init__(self):
		self.started = False

	def start(self):
		self.started = True

class AlphaCircularService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, bravo_circular_service: 'BravoCircularService'):
		self.bravo_circular_service = bravo_circular_service

	def start(self):
		pass

class BravoCircularService(ServiceInjector):
	def __init__(self):
		self.started = False

	def injectService(self, alpha_circular_service: AlphaCircularService):
		self.alpha_circular_service = alpha_circular_service

	def start(self):
		pass

class TestServiceInjectionOrder(unittest.TestCase):

	def setUp(self):
		ServiceRegister.SERVICES_REGISTRED.clear()
		ServiceRegister.SERVICES_INSTANCES.clear()
		ServiceRegister.ORDERED_SERVICES = None

	@patch.object(CharlieService, 'start', autospec=True)
	@patch.object(BravoService, 'start', autospec=True)
	@patch.object(AlphaService, 'start', autospec=True)
	def test_simple_injection_order(self, mock_alpha_start: Mock, mock_bravo_start: Mock, mock_charlie_start: Mock):
		ServiceRegister.register_service(AlphaService.__name__, AlphaService)
		ServiceRegister.register_service(BravoService.__name__, BravoService)
		ServiceRegister.register_service(CharlieService.__name__, CharlieService)

		test_instance = self

		def alpha_start(self: AlphaService):
			self.started = True
			bravo = ServiceRegister.get_service(BravoService)
			test_instance.assertFalse(bravo.started)
		mock_alpha_start.side_effect = alpha_start

		def bravo_start(self: BravoService):
			self.started = True
			test_instance.assertTrue(self.alpha_service.started)
		mock_bravo_start.side_effect = bravo_start

		def charlie_start(self: CharlieService):
			self.started = True
			alpha = ServiceRegister.get_service(AlphaService)
			bravo = ServiceRegister.get_service(BravoService)
			# Alpha was registered first
			test_instance.assertTrue(alpha.started)
			# Bravo was registered first but had a dependency,
			# whereas Charlie was registered later and had no dependencies.
			test_instance.assertFalse(bravo.started)
		mock_charlie_start.side_effect = charlie_start

		ServiceRegister.enable()

	@patch.object(GolfService, 'start', autospec=True)
	@patch.object(FoxtrotService, 'start', autospec=True)
	@patch.object(EchoService, 'start', autospec=True)
	@patch.object(DeltaService, 'start', autospec=True)
	@patch.object(CharlieService, 'start', autospec=True)
	@patch.object(BravoService, 'start', autospec=True)
	@patch.object(AlphaService, 'start', autospec=True)
	def test_complex_injection_order(self, mock_alpha_start: Mock, mock_bravo_start: Mock,
		mock_charlie_start: Mock, mock_delta_start: Mock, mock_echo_start: Mock,
		mock_foxtrot_start: Mock, mock_golf_start: Mock
	):
		ServiceRegister.register_service(AlphaService.__name__, AlphaService)
		ServiceRegister.register_service(BravoService.__name__, BravoService)
		ServiceRegister.register_service(CharlieService.__name__, CharlieService)
		ServiceRegister.register_service(DeltaService.__name__, DeltaService)
		ServiceRegister.register_service(EchoService.__name__, EchoService)
		ServiceRegister.register_service(FoxtrotService.__name__, FoxtrotService)
		ServiceRegister.register_service(GolfService.__name__, FoxtrotService)

		test_instance = self

		def alpha_start(self: AlphaService):
			self.started = True
			bravo = ServiceRegister.get_service(BravoService)
			test_instance.assertFalse(bravo.started)
			delta = ServiceRegister.get_service(DeltaService)
			test_instance.assertFalse(delta.started)
			echo = ServiceRegister.get_service(EchoService)
			test_instance.assertFalse(echo.started)
		mock_alpha_start.side_effect = alpha_start

		def bravo_start(self: BravoService):
			self.started = True
			test_instance.assertTrue(self.alpha_service.started)
		mock_bravo_start.side_effect = bravo_start

		def charlie_start(self: CharlieService):
			self.started = True
			echo = ServiceRegister.get_service(EchoService)
			test_instance.assertFalse(echo.started)
		mock_charlie_start.side_effect = charlie_start

		def delta_start(self: DeltaService):
			self.started = True
			test_instance.assertTrue(self.alpha_service.started)
			test_instance.assertTrue(self.bravo_service.started)
			test_instance.assertTrue(self.foxtrot_service.started)
		mock_delta_start.side_effect = delta_start

		def echo_start(self: EchoService):
			self.started = True
			test_instance.assertTrue(self.alpha_service.started)
			test_instance.assertTrue(self.charlie_service.started)
			foxtrot = ServiceRegister.get_service(FoxtrotService)
			test_instance.assertFalse(foxtrot.started)
		mock_echo_start.side_effect = echo_start

		def foxtrot_start(self: FoxtrotService):
			self.started = True
			test_instance.assertTrue(self.echo_service.started)
			delta = ServiceRegister.get_service(DeltaService)
			test_instance.assertFalse(delta.started)
		mock_foxtrot_start.side_effect = foxtrot_start

		def golf_start(self: GolfService):
			self.started = True
		mock_golf_start.side_effect = golf_start

		ServiceRegister.enable()

	def test_circular_dependency(self):
		ServiceRegister.register_service(AlphaCircularService.__name__, AlphaCircularService)
		ServiceRegister.register_service(BravoCircularService.__name__, BravoCircularService)

		ServiceRegister.create_services()

		with self.assertRaises(ServiceCicularDependencyException):
			ServiceRegister.determine_service_order()

	def test_missing_dependency(self):
		ServiceRegister.register_service(BravoService.__name__, BravoService)

		ServiceRegister.create_services()

		with self.assertRaises(ServiceNotRegisteredException):
			ServiceRegister.determine_service_order()

if __name__ == "__main__":
	unittest.main()
