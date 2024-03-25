import unittest
import queue_test

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromModule(queue_test)
	unittest.TextTestRunner(verbosity=2).run(suite)
