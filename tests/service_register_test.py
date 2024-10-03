from abc import ABC
from typing import cast
import unittest
from pyramid.api.services.tools.annotation import pyramid_service
from pyramid.api.services.tools.exceptions import ServiceAlreadyRegisterException, ServiceNotRegisteredException
from pyramid.api.services.tools.injector import ServiceInjector
from pyramid.api.services.tools.register import ServiceRegister

class IService(ABC):
	def __init__(self):
		self.name = "Carrot"

class AlphaService(ServiceInjector):
	pass

class BravoService(IService, ServiceInjector):
	def __init__(self):
		self.age = 21
		self.name = "Broccoli"

class CharlieService(IService, ServiceInjector):
	pass

class DeltaService(ServiceInjector):
	pass

class EchoService():
	pass

class FoxtrotService(ServiceInjector):
	pass

class ServiceRegisterDecoratorTest(unittest.TestCase):

	def setUp(self):
		ServiceRegister.SERVICES_REGISTRED.clear()
		ServiceRegister.SERVICES_INSTANCES.clear()
		ServiceRegister.ORDERED_SERVICES = None
		ServiceRegister.register_service(AlphaService.__name__, AlphaService)
		ServiceRegister.register_service(IService.__name__, BravoService)

	def test_service_registration(self):
		self.assertIsNotNone(ServiceRegister.get_service_registred(AlphaService.__name__))

	def test_service_interface_registration(self):
		self.assertIsNotNone(ServiceRegister.get_service_registred(IService.__name__))

	def test_service_interface(self):
		ServiceRegister.create_services()
		iservice = ServiceRegister.get_service(IService)
		beta_service = cast(BravoService, iservice)
		self.assertEqual(beta_service.age, 21)

	def test_service_interface_override(self):
		ServiceRegister.create_services()
		iservice = ServiceRegister.get_service(IService)
		beta_service = cast(BravoService, iservice)
		self.assertEqual(beta_service.name, "Broccoli")

	def test_register_duplicate_service(self):
		ServiceRegister.register_service(CharlieService.__name__, CharlieService)
		with self.assertRaises(ServiceAlreadyRegisterException):
			ServiceRegister.register_service(CharlieService.__name__, CharlieService)

	def test_register_duplicate_interface(self):
		with self.assertRaises(ServiceAlreadyRegisterException):
			ServiceRegister.register_service(IService.__name__, DeltaService)

	def test_register_not_baseclass(self):
		with self.assertRaises(TypeError):
			ServiceRegister.register_service(EchoService.__name__, EchoService)

	def test_can_get(self):
		ServiceRegister.create_services()
		ServiceRegister.get_service(AlphaService)

	def test_not_register(self):
		ServiceRegister.create_services()
		with self.assertRaises(ServiceNotRegisteredException):
			ServiceRegister.get_service(FoxtrotService)

	def test_not_register_str(self):
		ServiceRegister.create_services()
		with self.assertRaises(ServiceNotRegisteredException):
			ServiceRegister.get_service_registred(FoxtrotService.__class__.__name__)

	def test_class_not_register(self):
		ServiceRegister.create_services()
		with self.assertRaises(ServiceNotRegisteredException):
			ServiceRegister.get_service(BravoService)

if __name__ == "__main__":
	unittest.main()
