import atexit
import random
import string
import time

from tools.queue import Queue, QueueItem


THREADS_USE = 1
TIMES = 1
ITEM_DIFFUCULTY = 100


def generate_password(length):
	characters = string.ascii_letters + string.digits
	password = "".join(random.choice(characters) for _ in range(length))
	return password


def factorial(n):
	result = 1
	for i in range(1, n + 1):
		result *= i
	return result


def pi(n):
	start = time.time()

	for i in range(0, n):
		for x in range(1, 1000):
			3.141592 * 2**x
		for x in range(1, 10000):
			float(x) / 3.141592
		for x in range(1, 10000):
			float(3.141592) / x

	end = time.time()
	duration = end - start
	duration = round(duration, 3)
	return duration


results = [] * TIMES
q = Queue(THREADS_USE)


# Add functions to the queue
for item in range(TIMES):
	# q.add(QueueItem(item, factorial, lambda result: results.append(result), n=ITEM_DIFFUCULTY))
	q.add(QueueItem(item, pi, None, lambda result: results.append(result), n=ITEM_DIFFUCULTY))

start_time = time.time()

print(f"Starting {TIMES} times in {THREADS_USE} threads.")
q.start()

exit_handler_executed = False


def exit_handler():
	print("exit_handler")
	q.end()
	print("join")
	q.join()
	print("join exit")

	end_time = time.time()
	time_difference = end_time - start_time

	# print("\n".join(result))
	print(f"Execute in {time_difference} seconds, {len(results)} times in {THREADS_USE} threads.")

	average_benchmark = round(sum(results) / TIMES, 3)
	print(f"Average score (from {TIMES} repeats): {str(average_benchmark)}s")

	global exit_handler_executed
	exit_handler_executed = True


atexit.register(exit_handler)

while not exit_handler_executed:
	time.sleep(1)
