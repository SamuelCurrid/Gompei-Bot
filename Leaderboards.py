import discord
from discord.ext import commands

import os
import json
from datetime import datetime

defaultLeaderboard = {"server": {"lastUpdate": None, "messageLeaderboard": {}, "emojiLeaderboard": {}}, "quote": {"lastUpdate": None, "channelID": None, "leaderboard": {}}}

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
		serverLeaderboards = self.leaderboards[str(guild.id)]["server"]
		quoteLeaderboards = self.leaderboards[str(guild.id)]["quote"]

		if not message.author.bot:
			if str(message.author.id) not in serverLeaderboards["messageLeaderboard"]:
				serverLeaderboards["messageLeaderboard"][str(message.author.id)] = 1
			else:
				serverLeaderboards["messageLeaderboard"][str(message.author.id)] += 1

			if str(message.channel.id) == quoteLeaderboards["channelID"]:
				for user in message.mentions:
					if str(message.author.id) not in quoteLeaderboards["leaderboard"]:
						quoteLeaderboards["leaderboard"][str(message.author.id)] = 1
					else:
						quoteLeaderboards["leaderboard"][str(message.author.id)] += 1

		serverLeaderboards["lastUpdate"] = message.created_at.isoformat();
		quoteLeaderboards["lastUpdate"] = message.created_at.isoformat();
		await self.update_state()

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		guild = message.channel.guild
		serverLeaderboards = self.leaderboards[str(guild.id)]["server"]
		quoteLeaderboards = self.leaderboards[str(guild.id)]["quote"]

		if not message.author.bot:
			serverLeaderboards["messageLeaderboard"][str(message.author.id)] -= 1

			if str(message.channel.id) == quoteLeaderboards["channelID"]:
				for user in message.mentions:
					quoteLeaderboards["leaderboard"][str(message.author.id)] -= 1

		serverLeaderboards["lastUpdate"] = message.created_at.isoformat();
		quoteLeaderboards["lastUpdate"] = message.created_at.isoformat();
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
		leaderboard = self.leaderboards[str(guild.id)]["server"][self.cachedMessages[message.id]["type"]]

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

	async def update_leaderboards(self):
		"""
		Updates leaderboards from last run
		"""

		for guildID in self.leaderboards:
			serverLeaderboards = self.leaderboards[guildID]["server"]
			quoteLeaderboards = self.leaderboards[guildID]["quote"]

			lastServerUpdate = serverLeaderboards["lastUpdate"]
			lastQuotesUpdate = quoteLeaderboards["lastUpdate"]

			if serverLeaderboards["lastUpdate"] is not None:
				lastServerUpdate = datetime.fromisoformat(serverLeaderboards["lastUpdate"])

			if quoteLeaderboards["lastUpdate"] is not None:
				lastQuotesUpdate = datetime.fromisoformat(lastQuotesUpdate)

			for channel in self.bot.get_guild(int(guildID)).text_channels:
				# Catch exceptions for no permissions
				try:
					async for message in channel.history(limit=None, after=lastServerUpdate):
						if not message.author.bot:

							# Message leaderboard
							if str(message.author.id) not in serverLeaderboards["messageLeaderboard"]:
								serverLeaderboards["messageLeaderboard"][str(message.author.id)] = 1
							else:
								serverLeaderboards["messageLeaderboard"][str(message.author.id)] += 1

							if str(message.channel.id) == quoteLeaderboards["channelID"]:
								for user in message.mentions:
									if str(message.author.id) not in quoteLeaderboards["leaderboard"]:
										quoteLeaderboards["leaderboard"][str(message.author.id)] = 1
									else:
										quoteLeaderboards["leaderboard"][str(message.author.id)] += 1

				except discord.Forbidden:
					print("Do not have read message history permissions for: " + str(channel))

			serverLeaderboards["lastUpdate"] = datetime.utcnow().isoformat()
			quoteLeaderboards["lastUpdate"] = datetime.utcnow().isoformat()

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
				leaderboard = self.leaderboards[str(ctx.message.guild.id)]["quote"]["leaderboard"]
				leaderboardEmbed = embeds[leaderboardType]
			elif arg[0].lower() == "emojis":
				leaderboardType = "emojiLeaderboard"
				leaderboard = self.leaderboards[str(ctx.message.guild.id)]["server"]["emojiLeaderboard"]
				leaderboardEmbed = embeds[leaderboardType]
		else:
			leaderboardType = "messageLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["server"]["messageLeaderboard"]
			leaderboardEmbed = embeds[leaderboardType]

		leaderboardEmbed.clear_fields()

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
	async def set_quote_channel(self, ctx, arg):
		if ctx.message.author.guild_permissions.administrator:
			guild = ctx.message.guild

			for channel in ctx.message.channel_mentions:
				if self.leaderboards[str(guild.id)]["quote"]["channelID"] != str(channel.id):
					self.leaderboards[str(guild.id)]["quote"]["channelID"] = str(channel.id)
					self.leaderboards[str(guild.id)]["quote"]["lastUpdate"] = None

					await self.update_state()
					await self.update_leaderboards()

					return

	@commands.command(pass_context=True, name="reset")
	async def reset_leaderboard(self, ctx):
		if ctx.message.author.guild_permissions.administrator:
			guild = ctx.message.guild

			self.leaderboards[str(guild.id)]["server"]["lastUpdate"] = None
			self.leaderboards[str(guild.id)]["quote"]["lastUpdate"] = None

			self.leaderboards[str(guild.id)]["server"]["messageLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["server"]["quoteLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["quote"]["leaderboard"] = {}

			await self.update_state()
			await self.update_leaderboards()
			print("Got there")

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
