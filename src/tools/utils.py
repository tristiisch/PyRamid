# import asyncio
# import functools
import locale
import logging
import typing
import os

from enum import Enum
from typing import Optional
from datetime import datetime
from contextlib import contextmanager
# def to_thread(func: typing.Callable) -> typing.Coroutine:
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         return await asyncio.to_thread(func, *args, **kwargs)
#     return wrapper

def create_parent_directories(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)


def keep_latest_files(
	directory: str, num_to_keep: int = 10, except_prefixed: Optional[str] = None
) -> None:
	if not os.path.exists(directory):
		return

	files = [
		os.path.join(directory, f)
		for f in os.listdir(directory)
		if os.path.isfile(os.path.join(directory, f))
	]
	files.sort(key=os.path.getctime, reverse=True)

	for file in files[num_to_keep:]:
		basename = os.path.basename(file)
		if except_prefixed is not None and not basename.startswith(except_prefixed):
			try:
				os.remove(file)
			except OSError as e:
				logging.warning("Error occurred while removing %s due to %s", file, e)


def clear_directory(directory):
	if not os.path.exists(directory):
		return

	for filename in os.listdir(directory):
		file_path = os.path.join(directory, filename)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			logging.warning("Failed to delete %s due to %s", file_path, e)


def split_string_by_length(string, max_length) -> typing.Generator[str, None, None]:
	n = len(string)
	start = 0
	while start < n:
		end = min(n, start + max_length)
		if end < n:
			while end > start and string[end] != "\n":
				end -= 1
		yield string[start:end]
		start = end


def substring_with_end_msg(text, max_length, end_msg) -> tuple[str, bool]:
	if len(text) <= max_length:
		return text, False
	remaining_chars = len(text) - max_length
	substring = text[: max_length - len(end_msg.format(remaining_chars))]
	remaining_chars = len(text) - len(substring)
	return f"{substring}{end_msg.format(remaining_chars)}", True


def human_string_array(data, columns) -> str:
	col_widths = [max(len(str(x)) for x in column) for column in zip(*data, columns)]
	lines = [" | ".join((col.ljust(width) for col, width in zip(columns, col_widths)))]
	lines.append("-" * (sum(col_widths) + 3 * len(columns) - 1))
	for row in data:
		lines.append(" | ".join((str(col).ljust(width) for col, width in zip(row, col_widths))))
	return "\n".join(lines)

@contextmanager
def temp_locale(name):
	saved_locale = locale.setlocale(locale.LC_TIME)
	try:
		yield locale.setlocale(locale.LC_TIME, name)
	finally:
		locale.setlocale(locale.LC_TIME, saved_locale)

def format_date_by_country(date: datetime, country_code: str):
	country_codes = {
		'en-US': 'american_english',
		'en-GB': 'british_english',
		'bg': 'bulgarian',
		'zh-CN': 'chinese',
		'zh-TW': 'taiwan_chinese',
		'hr': 'croatian',
		'cs': 'czech',
		'id': 'indonesian',
		'da': 'danish',
		'nl': 'dutch',
		'fi': 'finnish',
		'fr': 'french',
		'de': 'german',
		'el': 'greek',
		'hi': 'hindi',
		'hu': 'hungarian',
		'it': 'italian',
		'ja': 'japanese',
		'ko': 'korean',
		'lt': 'lithuanian',
		'no': 'norwegian',
		'pl': 'polish',
		'pt-BR': 'brazil_portuguese',
		'ro': 'romanian',
		'ru': 'russian',
		'es-ES': 'spain_spanish',
		'sv-SE': 'swedish',
		'th': 'thai',
		'tr': 'turkish',
		'uk': 'ukrainian',
		'vi': 'vietnamese'
	}

	try:
		with temp_locale(country_code):
			formatted_date = date.strftime('%x')
			return formatted_date
	except locale.Error:
		logging.warning('Locale not available for %s (%s). Using default (en_US.utf8)', country_codes.get(country_code, "Unknown"), country_code)
		with temp_locale('en_US.utf8'):
			formatted_date = date.strftime('%x')
			return formatted_date

class Mode(Enum):
	PRODUCTION = 1
	PRE_PRODUCTION = 2
	DEVELOPMENT = 3
