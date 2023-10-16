
import asyncio
import functools
import typing
import os
import logging
import logging.handlers
import sys

# def to_thread(func: typing.Callable) -> typing.Coroutine:
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         return await asyncio.to_thread(func, *args, **kwargs)
#     return wrapper

def create_logger(file_name: str) -> logging.FileHandler:

	create_parent_directories(file_name)

	logs_handler = logging.handlers.RotatingFileHandler(
		filename = file_name,
		encoding="utf-8",
		mode="w",
		maxBytes=512 * 1024 * 1024, # 512 Mo
		backupCount=10
	)
	logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
	return logs_handler

def create_parent_directories(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)

def keep_latest_files(directory, num_to_keep=10):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=os.path.getctime, reverse=True)

    for file in files[num_to_keep:]:
        try:
            os.remove(file)
            print(f"Removed {file}")
        except OSError as e:
            print(f"Error: {e}")

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path} due to {e}")