import inspect
import locale
import logging
import os
import shutil
import typing
from contextlib import contextmanager
from datetime import datetime
from typing import Optional


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
		if os.path.isfile(os.path.join(directory, f)) and not f in ['.gitignore', '.gitkeep', '.dockerignore']
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

	i = 0
	for filename in os.listdir(directory):
		if filename in ['.gitignore', '.gitkeep', '.dockerignore']:
			continue
		file_path = os.path.join(directory, filename)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
				i = i + 1
		except Exception as e:
			logging.warning("Failed to delete file '%s' due to %s", file_path, e)
	logging.info("Cleared %d files from folder '%s'." % (i, directory))


def split_string_by_length(
	string, max_length: int, first_max_length=None, last_max_length=None
) -> typing.Generator[str, None, None]:
	n = len(string)
	start = 0
	end = min(n, start + (first_max_length or max_length))

	while start < n:
		if end < n:
			while end > start and string[end] != "\n":
				end -= 1
		yield string[start:end]

		start = end
		if start == n:
			break

		if start == 0:
			end = min(n, start + (first_max_length or max_length))
		elif start == n - 1:
			end = n
		else:
			end = min(n, start + max_length)

	if last_max_length:
		last_start = max(0, n - last_max_length)
		yield string[last_start:n]


def substring_with_end_msg(text: str, max_length: int, end_msg: str) -> tuple[str, bool]:
	if len(text) <= max_length:
		return text, False
	remaining_chars = len(text) - max_length
	substring = text[: max_length - len(end_msg.format(remaining_chars))]
	remaining_chars = len(text) - len(substring)
	return f"{substring}{end_msg.format(remaining_chars)}", True


def human_string_array(
	data: list[list[str]], columns: list[str], max_row_size: int | None = None
) -> str:
	# Calculate the original column sizes
	col_widths = [
		max(len(str(x)) if isinstance(x, str) else 0 for x in column)
		for column in zip(*data, columns)
	]

	# Check if reduction is needed
	if max_row_size is not None:
		# Reduce columns one by one in descending order of their original size
		sorted_columns = sorted(enumerate(col_widths), key=lambda x: x[1], reverse=True)

		for index, original_width in sorted_columns:
			# Calculate the proportional reduction factor based on the maximum row size
			scaling_factor = min(1, max_row_size / original_width)

			# Apply the reduction to the current column
			col_widths[index] = int(original_width * scaling_factor)

			# Ensure that the reduced size is within the bounds
			col_widths[index] = max(1, col_widths[index])

	# Build the table string using the calculated column sizes
	lines = [
		" │ ".join(
			(
				col
				if isinstance(col, int)
				else col[:width].ljust(width)
				if len(col) > width
				else col.ljust(width)
				for col, width in zip(columns, col_widths)
			)
		)
	]

	separator = "─┼─".join("─" * width for width in col_widths)
	lines.append(separator)

	# Add rows to the table with truncated column data
	for row in data:
		row_str = " │ ".join(
			(
				str(col)
				if isinstance(col, int)
				else col[:width].ljust(width)
				if len(col) > width
				else col.ljust(width)
				for col, width in zip(row, col_widths)
			)
		)
		lines.append(row_str)

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


def format_bytes_speed(bytes_per_second: float):
	units = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
	factor = 1000
	for unit in units:
		if bytes_per_second < factor:
			return f"{round(bytes_per_second)} {unit}"
		bytes_per_second /= factor

	return f"{round(bytes_per_second)} {units[-1]}"
