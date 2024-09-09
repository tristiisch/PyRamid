
import time
from discord import AppInfo, ClientUser, Color, Embed,  Interaction
from discord.user import BaseUser
from pyramid.connector.discord.commands.api.abc import AbstractCommand
from pyramid.connector.discord.commands.api.annotation import discord_command
from pyramid.connector.discord.commands.api.parameters import ParametersCommand
from pyramid.data.environment import Environment
from pyramid.data.functional.application_info import ApplicationInfo
from pyramid.tools import utils

@discord_command(parameters=ParametersCommand(description="About the bot"))
class AboutCommand(AbstractCommand):

	# def __init__(self, bot: Bot, logger: logging.Logger, started: float, environment: Environment, info: ApplicationInfo):
	# 	super().__init__(bot, logger)
	# 	self.__started = started
	# 	self.__environment = environment
	# 	self.__info = info

	def injectService(self, environment: Environment, info: ApplicationInfo):
		self.__environment = environment
		self.__info = info
		# self.logger.info("Injected !")

	async def execute(self, ctx: Interaction):
		await ctx.response.defer(thinking=True)
		bot_user: ClientUser | None
		if self.bot.user is not None:
			bot_user = self.bot.user
		else:
			bot_user = None
			self.logger.warning("Unable to get self user instance")

		info = self.__info
		embed = Embed(title=info.get_name(), color=Color.gold())
		if bot_user is not None and bot_user.avatar is not None:
			embed.set_thumbnail(url=bot_user.avatar.url)

		owner_id: int | None = self.bot.owner_id
		if owner_id is None and self.bot.owner_ids is not None and len(self.bot.owner_ids) > 0:
			owner_id = next(iter(self.bot.owner_ids))
		else:
			owner_id = None

		owner: BaseUser | None
		if owner_id is not None:
			owner = await self.bot.fetch_user(owner_id)
		else:
			owner = None

		if owner is None:
			t: AppInfo = await self.bot.application_info()
			if t.team is not None:
				team = t.team
				if team.owner is not None:
					owner = team.owner

		if owner is not None:
			embed.set_footer(
				text=f"Owned by {owner.display_name}",
				icon_url=owner.avatar.url if owner.avatar is not None else None,
			)

		embed.add_field(name="Version", value=info.get_version(), inline=True)
		embed.add_field(name="OS", value=info.get_os(), inline=True)
		embed.add_field(
			name="Environment",
			value=self.__environment.name.capitalize(),
			inline=True,
		)
		embed.add_field(
			name="Uptime",
			value=utils.time_to_duration(int(round(time.time() - self.__info.get_started_at()))),
			inline=True,
		)

		await ctx.followup.send(embed=embed)
