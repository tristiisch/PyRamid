class CustomException(Exception):
	def __init__(self, *args: object):
		super().__init__(*args)


class DiscordMessageException(CustomException):
	def __init__(self, *args: object):
		msg = str(args[0]) % args[1:]
		super().__init__(msg)
