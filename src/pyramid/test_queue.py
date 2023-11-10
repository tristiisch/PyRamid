import atexit
import random
import string
import time

from tools.queue import Queue, QueueItem


THREADS_USE = 20
TIMES = 100_000
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

	q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
	decimal_output = ""

	for _ in range(n):
		if 4*q+r-t < m*t:
			decimal_output += str(m)
			if len(decimal_output) == 1:
				decimal_output += '.'
			nr = 10*(r - m*t)
			m = ((10*(3*q+r))//t)-10*m
			q *= 10
			r = nr
			decimal_output += str(m)
			t = t
		else:
			nr = (2*q+r)*x
			nn = (7*q*k+2+r*x)//(x*t)
			q *= k
			t *= x
			x += 2
			k += 1
			m = nn
			r = nr
	
	# print("PI", decimal_output)

	end = time.time()
	duration = end - start
	duration = round(duration, 3)
	return duration

results = [] * TIMES
q = Queue(THREADS_USE)


# Add functions to the queue
for item in range(TIMES):
	# q.add(QueueItem(item, factorial, lambda result: results.append(result), n=ITEM_DIFFUCULTY))
	q.add(
		QueueItem(
			item,
			pi,
			None,
			lambda result: results.append(result),
			n=ITEM_DIFFUCULTY,
		)
	)

print(f"Starting {TIMES} times in {THREADS_USE} threads with difficulty {ITEM_DIFFUCULTY}.")
q.start()
print("All thread started.")

start_time = time.time()

exit_handler_executed = False

# print("exit_handler")
q.end()

def exit_handler():
	global exit_handler_executed
	if exit_handler_executed:
		return

	# print("join")
	q.join()
	# print("join exit")

	end_time = time.time()
	time_difference = end_time - start_time

	# print("\n".join(result))
	print(f"Execute in {time_difference:.2f} seconds, {len(results)} times in {THREADS_USE} threads.")

	average_benchmark = round(sum(results) / TIMES, 3)
	print(f"Average score : {str(average_benchmark)}s")

	exit_handler_executed = True


atexit.register(exit_handler)
exit_handler()

# while not exit_handler_executed:
# 	time.sleep(1)
