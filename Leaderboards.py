import discord
from discord.ext import commands

import os
import json
from datetime import datetime

defaultLeaderboard = {"lastUpdate": None, "quotesChannel": None, "messageLeaderboard": {}, "emojiLeaderboard": {}, "quoteLeaderboard": {}}
embeds = {"messageLeaderboard": discord.Embed(title="Message leaderboard", colour=discord.Colour.red()), "emojiLeaderboard": discord.Embed(title="Emoji Usage Leaderboard", colour=discord.Colour.red()), "quoteLeaderboard": discord.Embed(title="Quotes Leaderboard", description="Calculated from mentions", colour=discord.Colour.red())}


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
		leaderboards = self.leaderboards[str(guild.id)]

		if not message.author.bot:
			if str(message.author.id) not in leaderboards["messageLeaderboard"]:
				leaderboards["messageLeaderboard"][str(message.author.id)] = 1
			else:
				leaderboards["messageLeaderboard"][str(message.author.id)] += 1

			if str(message.channel.id) == leaderboards["quotesChannel"]:
				for user in message.mentions:
					if str(user.id) not in leaderboards["quoteLeaderboard"]:
						leaderboards["quoteLeaderboard"][str(user.id)] = 1
					else:
						leaderboards["quoteLeaderboard"][str(user.id)] += 1

		leaderboards["lastUpdate"] = message.created_at.isoformat()
		await self.update_state()

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.channel.guild
		leaderboards = self.leaderboards[str(guild.id)]

		if not message.author.bot:
			leaderboards["messageLeaderboard"][str(message.author.id)] -= 1

			if str(message.channel.id) == leaderboards["quotesChannel"]:
				for user in message.mentions:
					leaderboards["quotesChannel"][str(user.id)] -= 1

		leaderboards["lastUpdate"] = message.created_at.isoformat()
		await self.update_state()

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if not user.bot:
			if reaction.message.id in self.cachedMessages:
				if reaction.emoji == "➡️":
					await self.update_leaderboard_message(reaction.message, 1)
					await reaction.remove(user)
				elif reaction.emoji == "⬅️":
					await self.update_leaderboard_message(reaction.message, -1)
					await reaction.remove(user)

	async def update_leaderboard_message(self, message, modifier):
		global embeds
		guild = message.channel.guild

		leaderboardEmbed = embeds[self.cachedMessages[message.id]["type"]]
		leaderboard = self.leaderboards[str(guild.id)][self.cachedMessages[message.id]["type"]]

		page = self.cachedMessages[message.id]["page"]

		if len(leaderboard) / 10 + 1 >= page + modifier > 0:
			page += modifier
			scores = await self.score_leaderboard(guild, leaderboard)
			leaderboardEmbed.clear_fields()
			leaderboardEmbed.add_field(name="User", value="".join(scores.split("\t")[(page - 1) * 10:page * 10]), inline=True)
			await message.edit(embed=leaderboardEmbed)

			self.cachedMessages[message.id]["page"] += modifier

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

		await self.update_state()

	async def update_leaderboards(self):
		"""
		Updates leaderboards from last run
		"""

		for guildID in self.leaderboards:
			leaderboard = self.leaderboards[guildID]
			lastUpdate = leaderboard["lastUpdate"]

			if leaderboard["lastUpdate"] is not None:
				lastUpdate = datetime.fromisoformat(leaderboard["lastUpdate"])

			for channel in self.bot.get_guild(int(guildID)).text_channels:

				# Catch exceptions for no permissions
				try:
					async for message in channel.history(limit=None, after=lastUpdate):
						if not message.author.bot:

							# Message leaderboard
							if str(message.author.id) not in leaderboard["messageLeaderboard"]:
								leaderboard["messageLeaderboard"][str(message.author.id)] = 1
							else:
								leaderboard["messageLeaderboard"][str(message.author.id)] += 1

							# Quote leaderboard
							if str(message.channel.id) == leaderboard["quotesChannel"]:
								for user in message.mentions:
									if str(user.id) not in leaderboard["quoteLeaderboard"]:
										leaderboard["quoteLeaderboard"][str(user.id)] = 1
									else:
										leaderboard["quoteLeaderboard"][str(user.id)] += 1

				except discord.Forbidden:
					print("Do not have read message history permissions for: " + str(channel))

			leaderboard["lastUpdate"] = datetime.utcnow().isoformat()

		await self.update_state()
		print("Got there")

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
	async def message_leaderboard(self, ctx, *arg):
		"""
		Creates a new message leaderboard
		"""
		global embeds
		guild = ctx.message.guild

		if len(arg) > 0:
			if arg[0].lower() == "quotes":
				leaderboardType = "quoteLeaderboard"
				leaderboard = self.leaderboards[str(ctx.message.guild.id)]["quoteLeaderboard"]
				leaderboardEmbed = embeds[leaderboardType]
			elif arg[0].lower() == "emojis":
				leaderboardType = "emojiLeaderboard"
				leaderboard = self.leaderboards[str(ctx.message.guild.id)]["emojiLeaderboard"]
				leaderboardEmbed = embeds[leaderboardType]
		else:
			leaderboardType = "messageLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["messageLeaderboard"]
			leaderboardEmbed = embeds[leaderboardType]

		leaderboardEmbed.clear_fields()

		leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda a: a[1], reverse=True)}
		leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda a: a[1], reverse=True)}

		pastScore = 0
		offset = 0
		position = 0
		userValues = ""

		for participant in leaderboard:
			score = leaderboard[participant]

			if score == pastScore:
				offset += 1
			else:
				position += offset + 1
				offset = 0
				pastScore = score

			username = ""
			if guild.get_member(int(participant)) is None:
				username = str(self.bot.get_user(int(participant)))
			else:
				username = str(guild.get_member(int(participant)).display_name)

			userValues += "**" + str(position) + ". " + username + "** - " + str(score) + "\n\n\t"

		if userValues == "":
			userValues = "None"

		leaderboardEmbed.add_field(name="User", value="".join(userValues.split("\t")[0:10]), inline=True)

		message = await ctx.send(embed=leaderboardEmbed)
		self.cachedMessages[message.id] = {"type": leaderboardType, "page": 1}
		await message.add_reaction("⬅️")
		await message.add_reaction("➡️")

	@commands.command(pass_context=True, name="set")
	async def set_quote_channel(self, ctx):
		if ctx.message.author.guild_permissions.administrator:
			guild = ctx.message.guild

			for channel in ctx.message.channel_mentions:
				if self.leaderboards[str(guild.id)]["quotesChannel"] != str(channel.id):
					self.leaderboards[str(guild.id)]["quotesChannel"] = str(channel.id)

					print("Updating guild " + str(guild.id) + " to use quotes channel " + str(channel.id))

					# REPLACE THIS WITH SEARCH FOR QUOTES CHANNEL, THIS DOES A FULL RESET
					self.leaderboards[str(guild.id)]["quoteLeaderboard"] = {}
					self.leaderboards[str(guild.id)]["lastUpdate"] = None

					async for message in guild.get_channel(channel.id).history(limit=None):
						if not message.author.bot:
							for user in message.mentions:
								if str(user.id) not in self.leaderboards[str(guild.id)]["quoteLeaderboard"]:
									self.leaderboards[str(guild.id)]["quoteLeaderboard"][str(user.id)] = 1
								else:
									self.leaderboards[str(guild.id)]["quoteLeaderboard"][str(user.id)] += 1

					await self.update_state()
					print("Finished updating quotes channel")

	@commands.command(pass_context=True, name="reset")
	async def reset_leaderboard(self, ctx):
		"""
		Resets all leaderboard information. Requires admin perms
		"""

		if ctx.message.author.guild_permissions.administrator:
			guild = ctx.message.guild

			print("Resetting leaderboards for " + str(guild.id))

			self.leaderboards[str(guild.id)]["lastUpdate"] = None

			self.leaderboards[str(guild.id)]["messageLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["emojiLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["quoteLeaderboard"] = {}

			await self.update_state()
			await self.update_leaderboards()
			print("Successfully reset leaderboards")

	async def score_leaderboard(self, guild, leaderboard):
		leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda a: a[1], reverse=True)}

		pastScore = 0
		offset = 0
		position = 0
		userValues = ""

		for participant in leaderboard:
			score = leaderboard[participant]

			if score == pastScore:
				offset += 1
			else:
				position += offset + 1
				offset = 0
				pastScore = score

			if guild.get_member(int(participant)) is None:
				username = str(self.bot.get_user(int(participant)))
			else:
				username = str(guild.get_member(int(participant)).display_name)

			userValues += "**" + str(position) + ". " + username + "** - " + str(score) + "\n\n\t"

		if userValues == "":
			userValues = "None"

		return userValues
