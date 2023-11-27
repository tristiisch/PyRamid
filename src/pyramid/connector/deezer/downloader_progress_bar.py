import logging
import time
from pydeezer.ProgressHandler import BaseProgressHandler


def convert_bytes_to_appropriate_unit(bytes_per_second):
	units = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
	factor = 1000
	for unit in units:
		if bytes_per_second < factor:
			return f"{round(bytes_per_second)} {unit}"
		bytes_per_second /= factor

	return f"{round(bytes_per_second)} {units[-1]}"


class DownloaderProgressBar(BaseProgressHandler):
	def __init__(self):
		pass

	def initialize(self, *args, **kwargs):
		super().initialize(*args)
		self.current_chunk_size: int
		self.total_size: int

		self.start_time = time.time()
		self.last_print = self.start_time
		logging.info("Start download\t%s (%s)", self.track_title, self.track_quality)

	def update(self, *args, **kwargs):
		super().update(**kwargs)
		self.log_progress()

	def close(self, *args, **kwargs):
		if "size_downloaded" in kwargs:
			self.size_downloaded = kwargs["size_downloaded"]

		total_time = time.time() - self.start_time
		average_speed = self.size_downloaded / total_time
		logging.info(
			"End download\t%s in %.2f seconds - %s",
			self.track_title,
			total_time,
			convert_bytes_to_appropriate_unit(average_speed),
		)

	def log_progress(self):
		current_time = time.time()
		percentage = self.size_downloaded / self.total_size * 100
		duration_last_print = current_time - self.last_print
		if duration_last_print < 1:
			return

		duration = current_time - self.start_time
		if duration == 0:
			return

		current_speed = self.current_chunk_size / duration
		remaining_size = self.total_size - self.size_downloaded
		time_remaining = remaining_size / current_speed if current_speed > 0 else 0

		if percentage == 100:
			return

		logging.info(
			"Downloading %s %.2f%% - %s - %.2f seconds remaining",
			self.track_title,
			percentage,
			convert_bytes_to_appropriate_unit(current_speed),
			time_remaining,
		)
		self.last_print = current_time
