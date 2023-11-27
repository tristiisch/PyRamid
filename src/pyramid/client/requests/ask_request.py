class AskRequest:
	def __init__(self, action: str, data: str | None = None) -> None:
		self.action = action
		self.data = data
