class CustomException(Exception):
	def __init__(self, *args: object):
		msg = str(args[0]) % args[1:]
		self.msg = msg
		super().__init__(msg)


class DiscordMessageException(CustomException):
	pass


class EngineSourceNotFoundException(DiscordMessageException):
	pass

class TrackNotFoundException(DiscordMessageException):
	pass

class DeezerTokenException(CustomException):
    pass

class DeezerTokenInvalidException(DeezerTokenException):
	pass

class DeezerTokensUnavailableException(DeezerTokenException):
    pass

class DeezerTokenOverflowException(DeezerTokenException):
    pass

class RessourceNotExistsException(DiscordMessageException):
	pass

class RessourceBadFormatException(DiscordMessageException):
	pass
