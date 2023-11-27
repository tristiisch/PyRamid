from data.functional.git_info import GitInfo


git_info = GitInfo.read()
if git_info is None:
	git_info = GitInfo()
	git_info.get()

print(git_info.to_json())
