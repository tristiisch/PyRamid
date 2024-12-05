from abc import abstractmethod


class ISocketServerService:

	@abstractmethod
	async def open(self):
		pass

	@abstractmethod
	def close(self):
		pass
