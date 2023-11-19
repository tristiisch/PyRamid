class HealthModules:
	def __init__(
		self,
		configuration: bool = False,
		# spotify: bool = False,
		# deezer: bool = False,
		discord: bool = False,
		database: bool = False,
	) -> None:
		self.configuration = configuration
		# self.spotify = spotify
		# self.deezer = deezer
		self.discord = discord
		self.database = database

	def is_ok(self) -> bool:
		return (
			self.configuration and
			# self.spotify and
			# self.deezer and
			self.discord and
			self.database
		)
