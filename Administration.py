import discord
import json
import os
from discord.ext import commands
from datetime import datetime


class Administration(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.logs = {}
		self.load_state()
		self.embed = discord.Embed(colour=discord.Colour.blue())

	@commands.Cog.listener()
	async def on_ready(self):
		"""
		Loads leaderboard states
		"""
		await self.update_guilds()

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""
		Creates default settings for new guilds
		"""

		self.logs["guildSettings"][str(guild.id)] = None
		await self.update_state()

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		"""
		Removes guild settings for logging
		"""
		self.logs["guildSettings"].pop(str(guild.id))
		await self.update_state()

	@commands.command(pass_context=True)
	async def echo(self, ctx, arg1, *, arg2):
		channel = ctx.guild.get_channel(int(arg1[2:-1]))

		images = []

		if len(ctx.message.attachments) > 0:
			for i in ctx.message.attachments:
				images.append(await i.to_file())

		if channel is not None and ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 87585011070414848:
			await channel.send(arg2, files=images)

	async def update_guilds(self):

		savedGuilds = []
		for guildID in self.logs["guildSettings"]:
			savedGuilds.append(guildID)

		guilds = []
		for guild in self.bot.guilds:
			guilds.append(str(guild.id))

		addGuilds = [x for x in guilds if x not in savedGuilds]
		removeGuilds = [x for x in savedGuilds if x not in guilds]

		# Add new guilds
		for guildID in addGuilds:
			self.logs["guildSettings"][str(guildID)] = None

		# Remove disconnected guilds
		for guildID in removeGuilds:
			if guildID != "guildSettings":
				self.logs["guildSettings"].pop(str(guildID))

		await self.update_state()


	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		for activity in after.activities:
			foundActivity = False

			if type(activity) is discord.activity.CustomActivity:
				foundActivity = True

				# Check new status
				status = ""
				if activity.emoji is not None:
					if activity.emoji.is_custom_emoji():
						status += "<:" + str(activity.emoji.name) + ":" + str(activity.emoji.id) + "> "
					else:
						status += activity.emoji.name + " "
				if activity.name is not None:
					status += activity.name

				# Compare status before and after member update
				if str(after.id) not in self.logs:
					self.logs[str(after.id)] = status

					await self.send_status_log(after, "None", status)
					await self.update_state()

				elif self.logs[str(after.id)] != status:
					await self.send_status_log(after, str(self.logs[str(after.id)]), status)
					self.logs[str(after.id)] = status
					await self.update_state()

			if not foundActivity:
				if str(after.id) not in self.logs:
					self.logs[str(after.id)] = None
					await self.update_state()

				if self.logs[str(after.id)] is not None:
					await self.send_status_log(after, str(self.logs[str(after.id)]), None)
					self.logs[str(after.id)] = None
					await self.update_state()

			break

	async def update_state(self):
		with open(os.path.join("config", "logging.json"), "r+") as loggingFile:
			loggingFile.truncate(0)
			loggingFile.seek(0)
			json.dump(self.logs, loggingFile, indent=4)

	def load_state(self):
		with open(os.path.join("config", "logging.json"), "r+") as loggingFile:
			logs = loggingFile.read()
			self.logs = json.loads(logs)

	async def send_status_log(self, user, before, after):
		if self.logs["guildSettings"][str(user.guild.id)] is not None:
			channel = user.guild.get_channel(int(self.logs["guildSettings"][str(user.guild.id)]))

			self.embed.clear_fields()
			self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
			self.embed.add_field(name="**Custom status update**", value="\n**Before:** " + str(before) + "\n**After:** " + str(after))
			self.embed.set_footer(text="ID: " + str(user.id) + " • ")

			await channel.send(embed=self.embed)

	@commands.command(pass_context=True, name="logging")
	async def change_logging(self, ctx):
		if ctx.message.author.guild_permissions.administrator:
			for channel in ctx.message.channel_mentions:
				if self.logs["guildSettings"][str(ctx.message.guild.id)] != str(channel.id):
					self.logs["guildSettings"][str(ctx.message.guild.id)] = str(channel.id)

					print("Updating guild " + str(ctx.message.guild.id) + " to use logging channel " + str(channel.id))

					await self.update_state()
					print("Finished updating logging channel")
