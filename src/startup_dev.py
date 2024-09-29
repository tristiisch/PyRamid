import debugpy

from startup import startup


def startup_dev():
	debugpy.listen(('0.0.0.0', 5678))
	# debugpy.wait_for_client()
	startup()

if __name__ == "__main__":
	startup_dev()
