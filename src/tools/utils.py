from enum import Enum

import asyncio
import functools
import logging
import typing
import os

# def to_thread(func: typing.Callable) -> typing.Coroutine:
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         return await asyncio.to_thread(func, *args, **kwargs)
#     return wrapper


def create_parent_directories(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)

def keep_latest_files(directory, num_to_keep=10, except_prefixed=None):
	if not os.path.exists(directory):
		return

	files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
	files.sort(key=os.path.getctime, reverse=True)

	for file in files[num_to_keep:]:
		if except_prefixed != None and not file.startswith(except_prefixed):
			try:
				os.remove(file)
			except OSError as e:
				logging.warning(f"Error occurred while removing {file} due to {e}", exc_info=True)

def clear_directory(directory):
	if not os.path.exists(directory):
		return

	for filename in os.listdir(directory):
		file_path = os.path.join(directory, filename)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			logging.warning(f"Failed to delete {file_path} due to {e}", exc_info=True)
			
def split_string_by_length(string, max_length) -> typing.Generator[str, None, None]:
	n = len(string)
	start = 0
	while start < n:
		end = min(n, start + max_length)
		if end < n:
			while end > start and string[end] != '\n':
				end -= 1
		yield string[start:end]
		start = end
		
def human_string_array(data, columns):
	col_widths = [max(len(str(x)) for x in column) for column in zip(*data, columns)]
	lines = [' | '.join((col.ljust(width) for col, width in zip(columns, col_widths)))]
	lines.append('-' * (sum(col_widths) + 3 * len(columns) - 1))
	for row in data:
		lines.append(' | '.join((str(col).ljust(width) for col, width in zip(row, col_widths))))
	return '\n'.join(lines)

class Mode(Enum):
	PRODUCTION = 1
	PRE_PRODUCTION = 2
	DEVELOPEMENT = 3