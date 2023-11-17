from datetime import datetime
import discord

from logging import Logger
from discord import (
	Guild,
	Member,
	Role,
	Status,
)
from discord.ext.commands import Bot
from data.functional.application_info import ApplicationInfo
from connector.database.user import User, UserHandler


class BotListener:
	def __init__(self, bot: Bot, logger: Logger, info: ApplicationInfo):
		self.__bot = bot
		self.__logger = logger
		self.__info = info

	def register(self):
		bot = self.__bot

		@bot.event
		async def on_ready():
			await bot.tree.sync()
			await bot.change_presence(
				status=Status.online,
				activity=discord.Activity(
					type=discord.ActivityType.listening,
					name=f"{self.__info.get_version()}",
				),
			)

			if bot.user is None:
				self.__logger.warning("Unable to get discord bot name")
			else:
				self.__logger.info("Discord bot name '%s'", bot.user.name)
			self.__logger.info("------ GUILDS ------")

			for guild in bot.guilds:
				self.show_info_guild(guild)
				self.__logger.info("----------------------")

			self.__logger.info("Checkings all members")
			uh = UserHandler()
			for guild in bot.guilds:
				async for member in guild.fetch_members(limit=None):
					UserHandler.save(User.from_discord_user(member._user), uh)
			self.__logger.info("Discord bot ready")

		@bot.event
		async def on_member_update(before, after):
			UserHandler.save(User.from_discord_user(after))

		@bot.event
		async def on_guild_join(guild: Guild):
			self.__logger.info("Bot join guild :")
			self.show_info_guild(guild)
			uh = UserHandler()
			async for member in guild.fetch_members(limit=None):
				UserHandler.save(User.from_discord_user(member._user), uh)

		@bot.event
		async def on_guild_remove(guild: Guild):
			self.__logger.info("Bot leave guild '%s'", guild.name)
			self.show_info_guild(guild)

	def show_info_guild(self, guild: Guild):
		self.__logger.info(
			"'%s' has %d members. Creator is %s.",
			guild.name,
			guild.member_count,
			guild.owner,
		)

		if self.__bot.user is None:
			self.__logger.warning("Enable to get discord bot - Unable to get his roles")
		else:
			bot_member = guild.get_member(self.__bot.user.id)
			if bot_member is None:
				self.__logger.warning("  Enable to get discord bot role on %s", guild.name)
			else:
				self.__logger.info("  Bot roles :")
				for r in bot_member.roles:
					role: Role = r
					self.__logger.info("    '%s' ID %s", role.name, role.id)
