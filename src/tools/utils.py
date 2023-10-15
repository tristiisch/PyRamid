
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