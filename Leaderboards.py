import discord
from discord.ext import commands

import os
import json
from datetime import datetime

defaultLeaderboard = {"server": {"lastUpdate": None, "messageLeaderboard": {}, "emojisLeaderboard": {}}, "quotes": {"lastUpdate": None, "channelID": None, "leaderboard": {}}}


class Leaderboards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.leaderboards = {}
		self.cachedMessages = {}

	@commands.Cog.listener()
	async def on_ready(self):
		await self.load_state()
		await self.update_guilds()
		await self.update_leaderboards()


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		global defaultLeaderboard

		if str(guild.id) not in self.leaderboards:
			self.leaderboards[str(guild.id)] = defaultLeaderboard
			await self.update_state()

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		self.leaderboards.pop(str(guild.id))
		await self.update_state()

	@commands.Cog.listener()
	async def on_message(self, message):
		guild = message.channel.guild
		serverLeaderboards = self.leaderboards[str(guild.id)]["server"]["messageLeaderboard"]

		if not message.author.bot:
			if str(message.author.id) not in serverLeaderboards["messageLeaderboard"]:
				serverLeaderboards["messageLeaderboard"][str(message.author.id)] = 1
			else:
				serverLeaderboards["messageLeaderboard"][str(message.author.id)] += 1

			self.update_state()

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.channel.guild
		serverLeaderboards = messageLeaderboard = self.leaderboards[str(guild.id)]["server"]["messageLeaderboard"]

		if not message.author.bot:
			serverLeaderboards["messageLeaderboard"][str(message.author.id)] -= 1
			serverLeaderboards["lastUpdate"] = datetime.utcnow().isoformat()
			self.update_state()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if not user.bot:
			if reaction.message.id in self.cachedMessages:
				if reaction.emoji == "➡️":
					await self.increment_leaderboard(reaction.message)
					await reaction.remove(user)
				elif reaction.emoji == "⬅️":
					await self.decrement_leaderboard(reaction.message)
					await reaction.remove(user)

	async def increment_leaderboard(self, message):


	async def update_guilds(self):
		"""
		Updates guilds included in leaderboards.json
		"""

		global defaultLeaderboard

		savedGuilds = []
		for guildID in self.leaderboards:
			savedGuilds.append(int(guildID))

		guilds = []
		for guild in self.bot.guilds:
			guilds.append(guild.id)

		addGuilds = [x for x in guilds if x not in savedGuilds]
		removeGuilds = [x for x in savedGuilds if x not in guilds]

		# Add new guilds
		for guildID in addGuilds:
			self.leaderboards[str(guildID)] = defaultLeaderboard

		# Remove disconnected guilds
		for guildID in removeGuilds:
			self.leaderboards.pop(str(guildID))

	async def update_leaderboards(self):
		"""
		Updates leaderboards from last run
		"""

		for guildID in self.leaderboards:
			serverLeaderboards = self.leaderboards[guildID]["server"]
			lastUpdate = datetime.fromisoformat(self.leaderboards[guildID]["server"]["lastUpdate"])
			self.leaderboards[guildID]["server"]["lastUpdate"] = datetime.utcnow().isoformat()

			for channel in self.bot.get_guild(int(guildID)).text_channels:
				# Catch exceptions for no permissions
				try:
					async for message in channel.history(limit=None, after=lastUpdate):
						if not message.author.bot:

							# Message leaderboard
							if str(message.author.id) not in serverLeaderboards["messageLeaderboard"]:
								serverLeaderboards["messageLeaderboard"][str(message.author.id)] = 1
							else:
								serverLeaderboards["messageLeaderboard"][str(message.author.id)] += 1

				except discord.Forbidden:
					print("Do not have read message history permissions for: " + str(channel))

		await self.update_state()

	async def update_state(self):
		"""
		Saves current leaderboard information to leaderboards.json
		"""

		with open(os.path.join("config", "leaderboards.json"), "r+") as leaderboards:
			leaderboards.truncate(0)
			leaderboards.seek(0)
			json.dump(self.leaderboards, leaderboards, indent=4)

	async def load_state(self):
		"""
		Loads current saved leaderboard information from leaderboards.json
		"""

		with open(os.path.join("config", "leaderboards.json"), "r+") as leaderboards:
			self.leaderboards = json.loads(leaderboards.read())

	@commands.command(pass_context=True, name="leaderboard")
	async def message_leaderboard(self, ctx):
		"""
		Creates a new message leaderboard
		"""

		guild = ctx.message.guild
		messageLeaderboard = self.leaderboards[str(ctx.message.guild.id)]["server"]["messageLeaderboard"]
		leaderboardEmbed = discord.Embed(title="Message leaderboard", color=discord.Colour.red())

		messageLeaderboard = {k: v for k, v in sorted(messageLeaderboard.items(), key=lambda a: a[1], reverse=True)}

		pastScore = 0
		offset = 0
		position = 0
		userValues = ""

		for participant in messageLeaderboard:
			score = messageLeaderboard[participant]

			if score == pastScore:
				offset += 1
			else:
				position += offset + 1
				offset = 0
				pastScore = score

			username = ""
			if guild.get_member(int(participant)) is None:
				username = str(await self.bot.fetch_user(int(participant)))
			else:
				username = str(guild.get_member(int(participant)).display_name)

			userValues += "**" + str(position) + ". " + username + "** - " + str(score) + "\n\n\t"

		leaderboardEmbed.add_field(name="User", value="".join(userValues.split("\t")[0:10]), inline=True)

		message = await ctx.message.channel.send(embed=leaderboardEmbed)
		self.cachedMessages[message.id] = {"type": "messageLeaderboard", "page": 1}
		await message.add_reaction("⬅️")
		await message.add_reaction("➡️")
