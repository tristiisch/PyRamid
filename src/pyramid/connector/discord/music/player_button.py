import discord
from discord import ButtonStyle, Interaction
from discord.ui import Button

from pyramid.data.a_guild_cmd import AGuildCmd
from pyramid.data.functional.messages.message_sender_queued import MessageSenderQueued

class PlayerButton(discord.ui.View):
	def __init__(self, queue_action: AGuildCmd, timeout: float | None = 180):
		super().__init__(timeout=timeout)
		self.queue_action = queue_action

	@discord.ui.button(emoji="⏯️", style=ButtonStyle.primary)
	async def next_play_or_pause(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.resume_or_pause(ms, ctx)

	@discord.ui.button(emoji="⏭️", style=ButtonStyle.primary)
	async def next_track(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.next(ms, ctx)

	@discord.ui.button(emoji="🔀", style=ButtonStyle.primary)
	async def shuffle_queue(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.shuffle(ms, ctx)

	@discord.ui.button(emoji="⏹️", style=ButtonStyle.primary)
	async def stop_queue(self, ctx: Interaction, button: Button):
		ms = MessageSenderQueued(ctx)
		await ms.thinking()
		await self.queue_action.stop(ms, ctx)