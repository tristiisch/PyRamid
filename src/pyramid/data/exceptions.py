class CustomException(Exception):
	def __init__(self, *args: object):
		super().__init__(*args)


class DiscordMessageException(CustomException):
	def __init__(self, *args: object):
		self.msg = str(args[0]) % args[1:]
		super().__init__(self.msg)

class EngineSourceNotFoundException(DiscordMessageException):
	def __init__(self, *args: object):
		super().__init__(*args)

class TrackNotFoundException(DiscordMessageException):
	def __init__(self, *args: object):
		super().__init__(*args)
