import logging
from discord.ext.commands import Bot
from pyramid.connector.discord.services.api.injector import ServiceInjector


SERVICE_TO_REGISTER: dict[str, type[object]] = {}
SERVICE_REGISTRED: dict[str, object] = {}

def register_services(bot: Bot, logger: logging.Logger):
	for name, cls in SERVICE_TO_REGISTER.items():
		if issubclass(cls, ServiceInjector):
			class_instance = cls(bot, logger)
		else:
			class_instance = cls()
		SERVICE_REGISTRED[name] = class_instance
		logger.info("SERVICE_REGISTRED %s" % name)

def get_service(name: str):
	return SERVICE_REGISTRED[name]

def define_bot(bot: Bot):
	for _, instance in SERVICE_REGISTRED.items():
		if isinstance(instance, ServiceInjector):
			instance.bot = bot
