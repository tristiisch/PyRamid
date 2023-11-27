class HealthModules:
	def __init__(self, configuration: bool = False, discord: bool = False) -> None:
		self.configuration = configuration
		self.discord = discord

	def is_ok(self) -> bool:
		return self.configuration and self.discord
