from discord.flags import flag_value

class CustomException(Exception):
	def __init__(self, *args: object):
		if args:
			self.msg = str(args[0]) % args[1:]
		super().__init__(*args)


class DiscordMessageException(CustomException):
	pass


class EngineSourceNotFoundException(DiscordMessageException):
	pass


class TrackNotFoundException(DiscordMessageException):
	pass

class MissingPermissionException(DiscordMessageException):
	def __init__(self, permission_needed: flag_value, *args: object):
		super().__init__(*args)
		self.permission_needed = permission_needed

	def get_message(self):
		return ":warning: The bot lacks the necessary permissions %s." % self.permission_needed
