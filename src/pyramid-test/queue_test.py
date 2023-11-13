
import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyramid.tools.queue import Queue, QueueItem  # noqa: E402


class TestQueue(unittest.TestCase):
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

        with patch.object(Queue, 'join') as mock_join:
            Queue.wait_for_end(timeout_per_threads=5)
            mock_join.assert_called_with(5)

if __name__ == "__main__":
    unittest.main(failfast=True)
