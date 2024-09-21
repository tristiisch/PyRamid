import warnings

import aiofiles
import aiohttp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, modes

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	from cryptography.hazmat.primitives.ciphers.algorithms import Blowfish

from pydeezer.ProgressHandler import BaseProgressHandler


class DecryptDeezer:
	def __init__(self, blowfish_key: bytes, progress_handler: BaseProgressHandler) -> None:
		self.chunk_length = 6144
		self.decrypt_chunk_length = 2048
		self.cipher = Cipher(
			Blowfish(blowfish_key),
			modes.CBC(bytes([i for i in range(8)])),
			default_backend(),
		)
		self.progress_handler = progress_handler

	async def output_file(self, filesize: int, file_path: str, res: aiohttp.ClientResponse):
		async with aiofiles.open(file_path, "wb") as f:
			await f.seek(0)

			chunk_index = 0
			downloaded_size = 0
			previous_chunk = None
			async for chunk, _ in res.content.iter_chunks():
				chunk_size = len(chunk)
				self.progress_handler.update(current_chunk_size=chunk_size)

				downloaded_size += chunk_size
				if previous_chunk:
					previous_chunk, chunks_used = await self._transform_chunk(
						f, previous_chunk + chunk
					)
				else:
					previous_chunk, chunks_used = await self._transform_chunk(f, chunk)
				chunk_index += chunks_used

			if previous_chunk:
				await self._write_file(f, previous_chunk)
			if downloaded_size != filesize:
				missing = filesize - downloaded_size
				raise Exception("[%s] %d bytes are missing" % (filesize, missing))

	async def _transform_chunk(
		self, f: aiofiles.threadpool.binary.AsyncBufferedIOBase, bytes_chunked: bytes
	) -> tuple[bytes, int] | tuple[None, int]:
		# Calculate the number of chunks needed
		length_bytes = len(bytes_chunked)
		chunks_nb = int(length_bytes / self.chunk_length) + 1

		# Iterate over the chunks and call the callback for each one
		for i in range(chunks_nb - 1):
			chunk = bytes_chunked[i * self.chunk_length : (i + 1) * self.chunk_length]
			await self._write_file(f, chunk)

		last_chunk_start = (chunks_nb - 1) * self.chunk_length
		last_chunk = bytes_chunked[last_chunk_start:]
		last_length = len(last_chunk)

		if last_length == self.chunk_length:
			await self._write_file(f, last_chunk)
			return None, chunks_nb
		elif last_length < self.chunk_length:
			return last_chunk, chunks_nb - 1
		raise Exception(
			"Last chunk has wrong size %d (under %d is excepted)", last_length, self.chunk_length
		)

	async def _write_file(
		self, f: aiofiles.threadpool.binary.AsyncBufferedIOBase, new_chunk: bytes
	):
		chunk_size = len(new_chunk)
		if self.decrypt_chunk_length > chunk_size:
			await f.write(new_chunk)
		else:
			chunk_to_decrypt = new_chunk[: self.decrypt_chunk_length]
			decryptor = self.cipher.decryptor()
			dec_data = decryptor.update(chunk_to_decrypt) + decryptor.finalize()
			await f.write(dec_data)
			await f.write(new_chunk[self.decrypt_chunk_length :])
