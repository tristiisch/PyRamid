from typing import List, Union
from discord import Color, Embed, Interaction
from discord.app_commands import Command, locale_str
from pyramid.connector.discord.commands.abstract_command import AbstractCommand

class HelpCommand(AbstractCommand):

	def description(self) -> Union[str, locale_str]:
		return "List all commands"

	async def execute(self, ctx: Interaction):
		await ctx.response.defer(thinking=True)
		all_commands: List[Command] = self.bot.tree.get_commands()  # type: ignore
		commands_dict = {command.name: command.description for command in all_commands}
		embed_template = Embed(title="List of every commands available", color=Color.gold())
		max_embed = 10
		max_fields = 25
		embeds = []

		for command, description in commands_dict.items():
			embed_template.add_field(name=command, value=description, inline=True)
			if len(embed_template.fields) == max_fields:
				embeds.append(embeds)
				embed_template.clear_fields()

		# Append the last embed if it's not empty
		if len(embed_template.fields) > 0:
			embeds.append(embed_template)

		for i in range(0, len(embeds), max_embed):
			embeds_chunk = embeds[i : i + max_embed]
			await ctx.followup.send(embeds=embeds_chunk)
