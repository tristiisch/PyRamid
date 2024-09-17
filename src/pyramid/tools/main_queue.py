from pyramid.tools.custom_queue import Queue


class MainQueue:
	instance: Queue

	@classmethod
	def init(cls):
		cls.instance = Queue(1, "MessageSender")
		cls.instance.create_threads()
		cls.instance.start()
		cls.instance.register_to_wait_on_exit()

