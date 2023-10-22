import tools.utils

from tools.object import Track, TrackMinimal


def tracks(list_of_track: list[TrackMinimal] | list[Track]) -> str:
	data = [
		[i + 1, track.author_name, track.name, track.album_title]
		for i, track in enumerate(list_of_track)
	]
	columns = ["n°", "Author", "Title", "Album"]
	hsa = tools.utils.human_string_array(data, columns)
	return hsa
