import uuid
from abc import abstractmethod
from typing import Generic, TypeVar

import discord
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued
from discord import Interaction, Member, User

T = TypeVar("T")


class SelectView(discord.ui.View, Generic[T]):
	def __init__(self, select_options: dict[T, discord.SelectOption], multiple: bool = False):
		super().__init__()

		options_len = len(select_options)

		self.options_defined: dict[str, T] = {}
		options: list[discord.SelectOption] = [] * options_len

		for t, option in select_options.items():
			option.value = str(uuid.uuid4())

			label = self.concat(option.label)
			if label:
				option.label = label
			if option.description:
				description = self.concat(option.description)
				if description:
					option.description = description

			self.options_defined[option.value] = t
			options.append(option)

		async def callback(interaction: Interaction):
			ms = MessageSenderQueued(interaction)
			await ms.thinking()

			value_selected: str = self.children[0].values[0]  # type: ignore
			t = self.options_defined[value_selected]
			await self.on_select(interaction.user, ms, t)
			if not multiple:
				self.stop()

		select = discord.ui.Select(options=options)
		select.callback = callback
		self.add_item(select)

	@abstractmethod
	async def on_select(cls, user: User | Member, ms: MessageSenderQueued, t: T):
		pass

	@staticmethod
	def concat(str: str):
		if 100 >= len(str):
			return None
		suffix = "..."
		return str[: 100 - len(suffix)] + suffix
