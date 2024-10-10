class PingSocket:
	def __init__(self, ok: bool):
		self.ok = ok

	def is_ok(self) -> bool:
		return self.ok
