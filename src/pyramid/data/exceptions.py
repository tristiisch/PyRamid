class CustomException(Exception):
	def __init__(self, *args: object):
		self.msg = str(args[0]) % args[1:]
		super().__init__(*args)


class DiscordMessageException(CustomException):
	pass

class EngineSourceNotFoundException(DiscordMessageException):
	pass

class TrackNotFoundException(DiscordMessageException):
	pass
