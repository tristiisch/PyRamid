from datetime import datetime
from typing import Any, Coroutine, Literal, Optional, Sequence, Union

from discord import AllowedMentions, Attachment, Embed, File, Guild, Interaction, InteractionMessage, VoiceClient

from discord.ui import View
from discord.abc import Snowflake
from discord.utils import MISSING

class TrackMinimal:
	def __init__(self, data):
		self.id : str = data['id']
		self.author_name : str = data['artist']['name']
		self.author_picture : str = data['artist']['picture_medium']
		# self.authors =  [element['ART_NAME'] for element in data["ARTISTS"]]
		self.name : str = data['title_short']
		self.album_title : str = data['album']['title']
		self.album_picture : str = data['album']['cover_big']
		# self.duration_seconds = data['DURATION']
		# self.duration = self.__format_duration(data['DURATION'])
		# self.file_size = data['FILESIZE']
		# self.date = data["DATE_START"]
		# self.file_local = file_path

	def get_full_name(self) -> str :
		return f"{self.author_name} - {self.name}"
	
	def format_duration(self, input : int) -> str :
		seconds = int(input)

		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)

		time_format = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

		if days > 0:
			time_format = "{:02}d ".format(days) + time_format

		if days == 0 and hours == 0:
			time_format = "{:02}:{:02}".format(minutes, seconds)

		return time_format
	
	def _format_date(self, input : str) -> str :
		date_object = datetime.strptime(input, "%Y-%m-%d")

		return date_object.strftime("%x")

class Track(TrackMinimal):
	def __init__(self, data, file_path):
		self.author_name : str = data['ART_NAME']
		self.author_picture : str = f"https://e-cdn-images.dzcdn.net/images/artist/{data['ART_PICTURE']}/512x512-000000-80-0-0.jpg"
		self.authors : list[str] = [element['ART_NAME'] for element in data["ARTISTS"]]
		self.name : str = data['SNG_TITLE']
		self.album_title : str = data['ALB_TITLE']
		self.album_picture : str = f"https://e-cdn-images.dzcdn.net/images/cover/{data['ALB_PICTURE']}/512x512-000000-80-0-0.jpg"
		self.actual_seconds : int = int(0)
		self.duration_seconds : int = int(data['DURATION'])
		self.duration : str = self.format_duration(int(data['DURATION']))
		self.file_size : int = int(data['FILESIZE'])
		self.date : str = self._format_date(data["PHYSICAL_RELEASE_DATE"])
		self.file_local : str = file_path

class TrackList:
	def __init__(self):
		self.__tracks : list[Track] = []

	def add_song(self, track : Track):
		self.__tracks.append(track)

	def add_songs(self, tracks : list[Track]):
		self.__tracks.extend(tracks)

	def is_empty(self) -> bool:
		return len(self.__tracks) == 0
	
	def get_song(self) -> Track:
		return self.__tracks[0]
	
	def remove_song(self):
		self.__tracks.pop(0)

class GuildData:
	def __init__(self, guild : Guild):
		self.guild : Guild = guild
		self.track_list: TrackList = TrackList()
		self.voice_client: VoiceClient = None

class MessageSender:
	def __init__(self, ctx: Interaction):
		self.ctx = ctx

	async def add_message(
        self,
        content: str = MISSING,
        *,
        username: str = MISSING,
        avatar_url: Any = MISSING,
        tts: bool = MISSING,
        ephemeral: bool = MISSING,
        file: File = MISSING,
        files: Sequence[File] = MISSING,
        embed: Embed = MISSING,
        embeds: Sequence[Embed] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        view: View = MISSING,
        thread: Snowflake = MISSING,
        thread_name: str = MISSING,
        wait: Literal[True],
        suppress_embeds: bool = MISSING,
        silent: bool = MISSING,
    ):
		self.ctx.followup.send(content, username = username, avatar_url = avatar_url, tts = tts,
						 ephemeral = ephemeral, file = file, files = files, embed = embed, embeds = embeds,
						 allowed_mention = allowed_mentions, view = view, thread = thread, thread_name = thread_name,
						 wait = wait, suppress_embeds = suppress_embeds, silent = silent)

	async def edit_message(self, 
        *,
        content: Optional[str] = MISSING,
        embeds: Sequence[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        attachments: Sequence[Union[Attachment, File]] = MISSING,
        view: Optional[View] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> Coroutine[Any, Any, InteractionMessage] :
		return await self.ctx.edit_original_response(content = content, embeds = embeds, embed = embed,
											   attachments = attachments, view = view, allowed_mentions = allowed_mentions)
