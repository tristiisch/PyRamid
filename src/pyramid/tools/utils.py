import inspect
import locale
import logging
import os
import shutil
import typing
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Optional


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


def clear_directory(directory: str):
	if not os.path.exists(directory):
		return

	for filename in os.listdir(directory):
		file_path = os.path.join(directory, filename)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			logging.warning("Failed to delete %s due to %s", file_path, e)


def split_string_by_length(string: str, max_length: int) -> typing.Generator[str, None, None]:
	n = len(string)
	start = 0
	while start < n:
		end = min(n, start + max_length)
		if end < n:
			while end > start and string[end] != "\n":
				end -= 1
		yield string[start:end]
		start = end


def substring_with_end_msg(text: str, max_length: int, end_msg: str) -> tuple[str, bool]:
	if len(text) <= max_length:
		return text, False
	remaining_chars = len(text) - max_length
	substring = text[: max_length - len(end_msg.format(remaining_chars))]
	remaining_chars = len(text) - len(substring)
	return f"{substring}{end_msg.format(remaining_chars)}", True


def human_string_array(data: list[list[Any]], columns: list[str]) -> str:
	col_widths = [max(len(str(x)) for x in column) for column in zip(*data, columns)]
	lines = [" | ".join((col.ljust(width) for col, width in zip(columns, col_widths)))]
	lines.append("-" * (sum(col_widths) + 3 * len(columns) - 1))
	for row in data:
		lines.append(" | ".join((str(col).ljust(width) for col, width in zip(row, col_widths))))
	return "\n".join(lines)


@contextmanager
def temp_locale(name: str):
	saved_locale = locale.setlocale(locale.LC_TIME)
	try:
		yield locale.setlocale(locale.LC_TIME, name)
	finally:
		locale.setlocale(locale.LC_TIME, saved_locale)


def format_date_by_country(date: datetime, country_code: str):
	country_codes = {
		"en-US": "american_english",
		"en-GB": "british_english",
		"bg": "bulgarian",
		"zh-CN": "chinese",
		"zh-TW": "taiwan_chinese",
		"hr": "croatian",
		"cs": "czech",
		"id": "indonesian",
		"da": "danish",
		"nl": "dutch",
		"fi": "finnish",
		"fr": "french",
		"de": "german",
		"el": "greek",
		"hi": "hindi",
		"hu": "hungarian",
		"it": "italian",
		"ja": "japanese",
		"ko": "korean",
		"lt": "lithuanian",
		"no": "norwegian",
		"pl": "polish",
		"pt-BR": "brazil_portuguese",
		"ro": "romanian",
		"ru": "russian",
		"es-ES": "spain_spanish",
		"sv-SE": "swedish",
		"th": "thai",
		"tr": "turkish",
		"uk": "ukrainian",
		"vi": "vietnamese",
	}

	try:
		with temp_locale(country_code):
			formatted_date = date.strftime("%x")
			return formatted_date
	except locale.Error:
		logging.warning(
			"Locale not available for %s (%s). Using default (en_US.utf8)",
			country_codes.get(country_code, "Unknown"),
			country_code,
		)
		with temp_locale("en_US.utf8"):
			formatted_date = date.strftime("%x")
			return formatted_date


def time_to_duration(time_in_sec: int) -> str:
	# Define the constants for conversion
	seconds_in_minute = 60
	minutes_in_hour = 60
	hours_in_day = 24
	days_in_month = 30
	seconds_in_day = seconds_in_minute * minutes_in_hour * hours_in_day
	seconds_in_month = seconds_in_day * days_in_month

	# Convert the total duration into months, days, minutes, and seconds
	months, remainder = divmod(time_in_sec, seconds_in_month)
	days, remainder = divmod(remainder, seconds_in_day)
	hours, remainder = divmod(remainder, seconds_in_minute * minutes_in_hour)
	minutes, seconds = divmod(remainder, seconds_in_minute)

	result: list[str] = []

	# Display the result
	if months > 0:
		if months == 1:
			result.append(f"{months} month")
		else:
			result.append(f"{months} months")

		if days == 1:
			result.append(f"{days} day")
		elif days > 1:
			result.append(f"{days} days")

	elif days > 0:
		if days == 1:
			result.append(f"{days} day")
		else:
			result.append(f"{days} days")

		if hours == 1:
			result.append(f"{hours} hour")
		elif hours > 1:
			result.append(f"{hours} hours")

	elif hours > 0:
		if hours == 1:
			result.append(f"{hours} hour")
		else:
			result.append(f"{hours} hours")

		if minutes == 1:
			result.append(f"{minutes} minute")
		if minutes > 1:
			result.append(f"{minutes} minutes")

	elif minutes > 0:
		if minutes == 1:
			result.append(f"{minutes} minute")
		else:
			result.append(f"{minutes} minutes")

		if seconds == 1:
			result.append(f"{seconds} second")
		if seconds > 1:
			result.append(f"{seconds} seconds")

	elif seconds > 0:
		if seconds == 1:
			result.append(f"{seconds} second")
		else:
			result.append(f"{seconds} seconds")
	else:
		return "now"
	return ", ".join(result)


def get_available_space(path: str = "."):
	total, used, free = shutil.disk_usage(path)
	return free


def count_public_variables(obj):
	attributes = inspect.getmembers(obj, lambda a: not (inspect.isroutine(a)))

	# Filter names that don't start with an underscore
	public_variables = [name for name, _ in attributes if not name.startswith("_")]

	# Return the count of public variables
	return len(public_variables)


def print_human_readable(obj):
	# Get the class name
	class_name = obj.__class__.__name__

	# Get a list of attributes and their values
	attributes = [
		(attr, getattr(obj, attr))
		for attr in dir(obj)
		if not callable(getattr(obj, attr)) and not attr.startswith("__")
	]

	# Filter out attributes with None or non-string values
	attributes = [(name, value) for name, value in attributes if value is not None and isinstance(value, (str, int, float, bool))]

	# Create the formatted string
	formatted_string = "%s(%s)" % (
		class_name,
		" ".join([f"{name}[{value}]" for name, value in attributes]),
	)

	# Print the result
	return formatted_string

def plurial_humain_readable(list: list):
	lenght_list = len(list)

	# Check if the list contains only strings
	if not all(isinstance(item, str) for item in list):
		# Convert non-string elements to strings
		list = [str(item) for item in list]

	if lenght_list != 1:
		sep = "\n- "
		prefix_sep = sep
	else:
		sep = ", "
		prefix_sep =  " "
	list_str = sep.join(list)
	return prefix_sep + list_str
