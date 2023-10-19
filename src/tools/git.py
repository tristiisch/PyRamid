import json
import os
import pathlib

class GitInfo:

	def __init__(self):
		self.commit_id: str | None = None
		self.branch: str | None = None
		self.last_author: str | None = None

	def get(self, base_path = None, max_length = 8):
		if not base_path:
			dir = pathlib.Path()
		else:
			dir = pathlib.Path(base_path)

		git_dir = dir / ".git"
		if not git_dir.exists():
			return None
		
		git_head = git_dir / "HEAD"
		if not git_head.exists():
			return None

		with (git_head).open("r") as head:
			ref = head.readline().split(" ")[-1].strip()

		git_ref = git_dir / ref
		if git_ref.exists():
			with (git_ref).open("r") as git_hash:
				commit_id = git_hash.readline().strip()
			self.commit_id = commit_id[:max_length]

		with (git_head).open("r") as f:
			head = f.read().strip()
			self.branch = head.split("ref: refs/heads/")[1]

		git_log_head = git_dir / "logs" / "HEAD"
		if git_log_head.exists():
			log_lines = git_log_head.read_text().strip().split('\n')
			self.last_author = log_lines[-1].split(' ')[2]

	def to_json(self):
		data = vars(self)
		return json.dumps(data, indent=4)

	def save(self, file_name="git_info.json"):
		data = vars(self)
		with open(file_name, "w") as f:
			json.dump(data, f, indent=4)

	@classmethod
	def read(cls, file_name="git_info.json"):
		if not os.path.exists(file_name):
			return None
		try:
			with open(file_name, "r") as f:
				data = json.load(f)
			# return cls(**data)
			git_info = cls()
			git_info.commit_id = data["commit_id"]
			git_info.branch = data["branch"]
			git_info.last_author = data["last_author"]
			return git_info

		except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
			return None
