import asyncio
import time


class RateLimiterAsync:
	def __init__(self, max_requests, time_interval):
		self.max_requests = max_requests
		self.time_interval = time_interval
		self.requests: list[float] = []
		self.lock = asyncio.Lock()

	def _clean_old_requests(self):
		current_time = time.time()
		self.requests = [t for t in self.requests if self.time_interval > current_time - t]

	async def _wait_if_needed(self):
		async with self.lock:
			self._clean_old_requests()
			if len(self.requests) >= self.max_requests:
				sleep_time = self.requests[0] + self.time_interval - time.time()
				if sleep_time > 0:
					# logging.warning("Detect Deezer RateLimit - wait %f secs", sleep_time)
					await asyncio.sleep(sleep_time)
					self._clean_old_requests()

	async def check(self):
		await self._wait_if_needed()

	async def add(self):
		async with self.lock:
			self.requests.append(time.time())
