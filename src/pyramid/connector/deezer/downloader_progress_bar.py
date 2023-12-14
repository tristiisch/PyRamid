import logging
import time
from pydeezer.ProgressHandler import BaseProgressHandler
from tools import utils


class DownloaderProgressBar(BaseProgressHandler):
	def __init__(self):
		pass

	def initialize(self, *args, **kwargs):
		super().initialize(*args)
		self.current_chunk_size: int
		self.size_downloaded: int
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
			utils.format_bytes_speed(average_speed),
		)

	def log_progress(self):
		return
		current_time = time.time()
		percentage = self.size_downloaded / self.total_size * 100
		duration_last_print = current_time - self.last_print
		if duration_last_print < 1:
			return

		duration = current_time - self.start_time
		if duration == 0:
			return

		current_speed = self.size_downloaded / duration
		remaining_size = self.total_size - self.size_downloaded
		time_remaining = round(remaining_size / current_speed) if current_speed > 0 else 0

		if percentage == 100:
			return

		logging.info(
			"Downloading %s %.2f%% - %s - %s remaining",
			self.track_title,
			percentage,
			utils.format_bytes_speed(current_speed),
			utils.time_to_duration(time_remaining),
		)
		self.last_print = current_time
