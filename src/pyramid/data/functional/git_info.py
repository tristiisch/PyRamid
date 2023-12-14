import json
import logging
import os
import pathlib


class GitInfo:
	def __init__(self):
		self.commit_id: str | None = None
		self.branch: str | None = None
		self.last_author: str | None = None

	def get(self, base_path=None, max_length=7) -> bool:
		if not base_path:
			directory = pathlib.Path()
		else:
			directory = pathlib.Path(base_path)

		git_dir = directory / ".git"
		if not git_dir.exists():
			return False

		git_head = git_dir / "HEAD"
		if not git_head.exists():
			return False

		ref = None
		commit_hash = None
		with (git_head).open("r") as f:
			head_file = f.read().strip()

			prefix = "ref: "
			if head_file.startswith(prefix):
				head_file = head_file[len(prefix) :]
				ref = head_file
				prefix = "refs/heads/"
				if head_file.startswith(prefix):
					head_file = head_file[len(prefix) :]
				self.branch = head_file

				git_ref = git_dir / ref
				if git_ref.exists():
					with (git_ref).open("r") as git_hash:
						commit_id = git_hash.readline().strip()
					self.commit_id = commit_id[:max_length]

			# Repo is in detached HEAD
			else:
				commit_hash = head_file
				self.commit_id = commit_hash[:max_length]

				heads_path = git_dir / "refs" / "heads"
				for root, dirs, files in os.walk(heads_path):
					for branch_name in files:
						branch_path = os.path.join(root, branch_name)
						with open(branch_path, "r") as branch_file:
							if branch_file.read().strip() == commit_hash:
								self.branch = os.path.relpath(branch_path, heads_path).replace(
									"\\", "/"
								)
								break
					if self.branch is not None:
						break

		git_log_head = git_dir / "logs" / "HEAD"
		if git_log_head.exists():
			log_lines = git_log_head.read_text().strip().split("\n")
			self.last_author = log_lines[-1].split(" ")[2]

		return True

	def to_json(self):
		data = vars(self)
		return json.dumps(data, indent=4)

	def save(self, file_name="git_info.json"):
		data = vars(self)
		with open(file_name, "w") as f:
			json.dump(data, f, indent=4)

	@classmethod
	def read(cls, file_name="git_info.json", max_length=8):
		if not os.path.exists(file_name):
			return None
		try:
			with open(file_name, "r") as f:
				data = json.load(f)
			git_info = cls()

			git_info.commit_id = data["commit_id"][:max_length]
			git_info.branch = data["branch"]
			git_info.last_author = data["last_author"]
			return git_info

		except (
			FileNotFoundError,
			json.JSONDecodeError,
			UnicodeDecodeError,
			TypeError,
		) as e:
			logging.warning("Error occurred while read %s due to %s", file_name, e)
			return None
