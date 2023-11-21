from typing import Self

import tools.utils
from connector.database.sql_methods import SQLMethods
# from data.track import TrackMinimalDeezer
from sqlalchemy import BigInteger, CheckConstraint, Column, Sequence, String, UniqueConstraint


class TrackStored(SQLMethods):
	__tablename__ = "tracks"

	id = Column(BigInteger, Sequence(f"{__name__.lower()}_id_seq"), primary_key=True)
	dl_id = Column(BigInteger, CheckConstraint("dl_id >= 0"), unique=True)
	name = Column(String)
	artist = Column(String)
	album = Column(String)

	__table_args__ = (UniqueConstraint("name", "artist", "album"),)

	def __str__(self):
		return tools.utils.print_human_readable(self)

	# @classmethod
	# def from_deezer_source(cls, track: TrackMinimalDeezer) -> Self:
	# 	return cls(
	# 		dl_id=track.id, name=track.name, artist=track.author_name, album=track.album_title
	# 	)
