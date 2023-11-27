import os
import sys
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyramid.tools.queue import Queue, QueueItem  # noqa: E402


class SimpleQueue(unittest.TestCase):
	def test_add(self):
		queue = Queue(threads=1)
		self.assertEqual(queue.length(), 0)

		item = QueueItem(name="test", func=lambda x: x, x=5)
		queue.add(item)
		self.assertEqual(queue.length(), 1)

	def test_add_at_start(self):
		queue = Queue(threads=1)
		self.assertEqual(queue.length(), 0)

		item = QueueItem(name="test", func=lambda x: x, x=5)
		queue.add_at_start(item)
		self.assertEqual(queue.length(), 1)

	def test_worker_start_before(self):
		queue = Queue(threads=1)
		self.assertEqual(queue.length(), 0)

		queue.start()
		item = QueueItem(name="test", func=lambda x: x, x=5)
		queue.add(item)
		self.assertEqual(queue.length(), 1)

		queue.end()
		queue.join()
		self.assertEqual(queue.length(), 0)

	def test_worker_start_after(self):
		queue = Queue(threads=1)
		self.assertEqual(queue.length(), 0)

		item = QueueItem(name="test", func=lambda x: x, x=5)
		queue.add(item)
		self.assertEqual(queue.length(), 1)

		queue.start()
		queue.end()
		queue.join()
		self.assertEqual(queue.length(), 0)

	def test_wait_for_end(self):
		queue = Queue(threads=1)
		queue.register_to_wait_on_exit()
		queue.start()

		item = QueueItem(name="test", func=lambda x: x, x=5)
		queue.add(item)

		Queue.wait_for_end(1)


class MediumQueue(unittest.TestCase):
	def test_order_simple(self):
		thread_nb = 1
		queue = Queue(threads=thread_nb)
		results = []
		results_excepted = list(range(1, 10))

		for i in range(1, 10):
			item = QueueItem(
				f"test{i}", lambda n: n, None, lambda result: results.append(result), n=i
			)
			queue.add(item)

		queue.start()
		queue.end()
		queue.join()

		self.assertEqual(results, results_excepted)

	def test_order_reverse(self):
		thread_nb = 1
		queue = Queue(threads=thread_nb)
		results = []
		results_excepted = list(range(9, 0, -1))

		for i in range(1, 10):
			item = QueueItem(
				f"test{i}", lambda n: n, None, lambda result: results.append(result), n=i
			)
			queue.add_at_start(item)

		queue.start()
		queue.end()
		queue.join()

		self.assertEqual(results, results_excepted)

	def test_order_mixed(self):
		thread_nb = 1
		queue = Queue(threads=thread_nb)
		results = []
		results_excepted = list(range(1, 100))

		for i in range(10, 20):
			item = QueueItem(
				f"test{i}", lambda n: n, None, lambda result: results.append(result), n=i
			)
			queue.add(item)

		for i in range(9, 0, -1):
			item = QueueItem(
				f"test{i}", lambda n: n, None, lambda result: results.append(result), n=i
			)
			queue.add_at_start(item)

		for i in range(20, 100):
			item = QueueItem(
				f"test{i}", lambda n: n, None, lambda result: results.append(result), n=i
			)
			queue.add(item)

		queue.start()
		queue.end()
		queue.join()

		self.assertEqual(results, results_excepted)

	def test_order_multi_thread(self):
		thread_nb = 10
		items = 100
		queue = Queue(threads=thread_nb)
		results = []
		results_excepted = list(range(1, items))

		def sleep_and_return_n(n):
			time.sleep(n / 1000)
			return n

		for i in range(1, items):
			item = QueueItem(
				f"test{i}", sleep_and_return_n, None, lambda result: results.append(result), n=i
			)
			queue.add(item)

		queue.start()
		queue.end()
		queue.join()

		self.assertEqual(results, results_excepted)

	def test_wait_for_end_shutdown_threads(self):
		thread_nb = 2
		timeout_per_thread = 1
		items = 100

		queue = Queue(threads=thread_nb)
		queue.register_to_wait_on_exit()

		for i in range(items):
			item = QueueItem(name=f"test{i}", func=lambda: time.sleep(60))
			queue.add(item)

		self.assertEqual(queue.length(), items)
		queue.start()
		start_time = time.time()

		queue.join(timeout_per_thread)

		end_time = time.time()
		elapsed_time = end_time - start_time
		self.assertLessEqual(elapsed_time, thread_nb * timeout_per_thread + 1)


if __name__ == "__main__":
	unittest.main(failfast=True)
