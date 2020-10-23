from Permissions import command_channels
from discord.ext import commands
from datetime import datetime

import discord
import json
import os


defaultLeaderboard = {"lastUpdate": None, "quotesChannel": None, "messageLeaderboard": {}, "reactionLeaderboard": {}, "emojiLeaderboard": {}, "quoteLeaderboard": {}}
embeds = {"messageLeaderboard": discord.Embed(title="Message leaderboard", colour=discord.Colour.red()), "reactionLeaderboard": discord.Embed(title="Reaction Usage Leaderboard", colour=discord.Colour.red()), "quoteLeaderboard": discord.Embed(title="Quotes Leaderboard", description="Calculated from mentions", colour=discord.Colour.red()), "emojiLeaderboard": discord.Embed(title="Emoji leaderboard", colour=discord.Colour.red())}


class Leaderboards(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.leaderboards = {}
		self.cachedMessages = {}

	@commands.Cog.listener()
	async def on_ready(self):
		"""
		Loads leaderboard states
		"""

		await self.load_state()
		await self.update_guilds()

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""
		Creates default settings for new guilds
		"""
		global defaultLeaderboard

		if str(guild.id) not in self.leaderboards:
			self.leaderboards[str(guild.id)] = defaultLeaderboard
			await self.update_state()

	@commands.Cog.listener()
	async def on_guild_emojis_update(self, before, after):

		emojiLeaderboard = self.leaderboards["emojiLeaderboard"]

		addEmoji = [x for x in after if x not in before]

		for emoji in addEmoji:
			emojiLeaderboard[str(emoji.id)] == 0

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		"""
		Removes guilds from the settings
		"""
		self.leaderboards.pop(str(guild.id))
		await self.update_state()

	@commands.Cog.listener()
	async def on_message(self, message):
		"""
		Updates leaderboards based on sent message content
		"""
		# If message was sent in a guild
		if isinstance(message.channel, discord.TextChannel):
			guild = message.channel.guild
			leaderboard = self.leaderboards[str(guild.id)]

			if not message.author.bot:
				# Check message author
				if str(message.author.id) not in leaderboard["messageLeaderboard"]:
					leaderboard["messageLeaderboard"][str(message.author.id)] = 1
				else:
					leaderboard["messageLeaderboard"][str(message.author.id)] += 1

				# Check for quotes
				if str(message.channel.id) == leaderboard["quotesChannel"]:
					for user in message.mentions:
						if str(user.id) not in leaderboard["quoteLeaderboard"]:
							leaderboard["quoteLeaderboard"][str(user.id)] = 1
						else:
							leaderboard["quoteLeaderboard"][str(user.id)] += 1

				# Check for emojis
				for emoji in self.bot.emojis:
					emojiName = "<:" + emoji.name + ":" + str(emoji.id) + ">"
					for index in range(0, message.content.count(emojiName)):
						leaderboard["emojiLeaderboard"][str(emoji.id)] += 1

			leaderboard["lastUpdate"] = message.created_at.isoformat()
			await self.update_state()

	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		"""
		Updates leaderboards based ond deleted message content
		"""
		if payload.guild_id is not None:
			guild = self.bot.get_guild(payload.guild_id)
			leaderboards = self.leaderboards[str(guild.id)]

			if payload.cached_message is not None:
				message = payload.cached_message

				if not message.author.bot:
					leaderboards["messageLeaderboard"][str(message.author.id)] -= 1

					if str(message.channel.id) == leaderboards["quotesChannel"]:
						for user in message.mentions:
							leaderboards["quotesChannel"][str(user.id)] -= 1

					for emoji in self.bot.emojis:
						emojiName = "<:" + emoji.name + ":" + str(emoji.id) + ">"
						for index in range(0, message.content.count(emojiName)):
							leaderboards["emojiLeaderboard"][str(emoji.id)] -= 1

				leaderboards["lastUpdate"] = message.created_at.isoformat()
				await self.update_state()

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		"""
		Updates reactions leaderboard and checks for leaderboard page changes
		"""

		guild = self.bot.get_guild(payload.guild_id)
		if guild is not None:
			channel = guild.get_channel(payload.channel_id)
			message = await channel.fetch_message(payload.message_id)
			user = guild.get_member(payload.user_id)

			# Update cached leaderboards
			if not payload.member.bot:
				if payload.message_id in self.cachedMessages:
					if payload.emoji.name == "➡️":
						await self.update_leaderboard_message(message, 1)
						await message.remove_reaction("➡️", user)
					elif payload.emoji.name == "⬅️":
						await self.update_leaderboard_message(message, -1)
						await message.remove_reaction("⬅️", user)

			# Update reaction leaderboards
			if not payload.member.bot:
				reactionLeaderboard = self.leaderboards[str(payload.guild_id)]["reactionLeaderboard"]

				if payload.emoji.id is not None:
					for guildEmoji in guild.emojis:
						if payload.emoji.id == guildEmoji.id:
							if ("<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">") not in reactionLeaderboard:
								reactionLeaderboard["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] = 1
							else:
								reactionLeaderboard["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] += 1

							break
				else:
					if payload.emoji.name not in reactionLeaderboard:
						reactionLeaderboard[str(payload.emoji.name)] = 1
					else:
						reactionLeaderboard[str(payload.emoji.name)] += 1

				if str(payload.emoji.id) in self.leaderboards[str(payload.guild_id)]["emojiLeaderboard"]:
					self.leaderboards[str(payload.guild_id)]["emojiLeaderboard"][str(payload.emoji.id)] += 1

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		"""
		Updates the reaction leaderboard
		"""

		guild = self.bot.get_guild(payload.guild_id)
		if guild is not None:
			# Update reaction leaderboards
			reactionLeaderboard = self.leaderboards[str(payload.guild_id)]["reactionLeaderboard"]

			if payload.emoji.id is not None:
				for guildEmoji in guild.emojis:
					if payload.emoji.id == guildEmoji.id:
						reactionLeaderboard["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] -= 1
						break

			else:
				reactionLeaderboard[str(payload.emoji.name)] -= 1

			if str(payload.emoji.id) in self.leaderboards[str(payload.guild_id)]["emojiLeaderboard"]:
				self.leaderboards[str(payload.guild_id)]["emojiLeaderboard"][str(payload.emoji.id)] -= 1

	async def update_leaderboard_message(self, message, modifier):
		"""
		Updates existing leaderboard message
		"""
		global embeds
		guild = message.channel.guild

		leaderboardEmbed = embeds[self.cachedMessages[message.id]["type"]]
		leaderboard = self.leaderboards[str(guild.id)][self.cachedMessages[message.id]["type"]]

		page = self.cachedMessages[message.id]["page"]

		if len(leaderboard) / 10 + 1 >= page + modifier > 0:
			page += modifier
			scores = await self.score_leaderboard(guild, leaderboard, self.cachedMessages[message.id]["type"])
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

							# Reaction + Emoji leaderboard
							for reaction in message.reactions:
								if type(reaction.emoji) is not str:
									if type(reaction.emoji) is not discord.partial_emoji.PartialEmoji:
										for guildEmoji in self.bot.get_guild(int(guildID)).emojis:
											if reaction.emoji.id == guildEmoji.id:
												if ("<:" + str(reaction.emoji.name) + ":" + str(reaction.emoji.id) + ">") not in leaderboard["reactionLeaderboard"]:
													leaderboard["reactionLeaderboard"]["<:" + str(reaction.emoji.name) + ":" + str(reaction.emoji.id) + ">"] = reaction.count
												else:
													leaderboard["reactionLeaderboard"]["<:" + str(reaction.emoji.name) + ":" + str(reaction.emoji.id) + ">"] += reaction.count

												break

									if str(reaction.emoji.id) in leaderboard["emojiLeaderboard"]:
										leaderboard["emojiLeaderboard"][str(reaction.emoji.id)] += reaction.count

								else:
									if str(reaction.emoji) not in leaderboard["reactionLeaderboard"]:
										leaderboard["reactionLeaderboard"][str(reaction.emoji)] = reaction.count
									else:
										leaderboard["reactionLeaderboard"][str(reaction.emoji)] += reaction.count

							# Emoji check
							for emoji in self.bot.emojis:
								emojiName = "<:" + emoji.name + ":" + str(emoji.id) + ">"
								for index in range(0, message.content.count(emojiName)):
									leaderboard["emojiLeaderboard"][str(emoji.id)] += 1

				except discord.Forbidden:
					print("Do not have read message history permissions for: " + str(channel))

			leaderboard["lastUpdate"] = datetime.utcnow().isoformat()

		await self.update_state()
		print("Leaderboards up to date")

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

	async def message_leaderboard(self, ctx, boardType):
		"""
		Creates a new message leaderboard
		"""

		global embeds
		guild = ctx.message.guild

		if boardType == "quotes":
			leaderboardType = "quoteLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["quoteLeaderboard"]
			leaderboardEmbed = embeds[leaderboardType]
		elif boardType == "reactions":
			leaderboardType = "reactionLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["reactionLeaderboard"]
			leaderboardEmbed = embeds[leaderboardType]
		elif boardType == "emojis":
			leaderboardType = "emojiLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["emojiLeaderboard"]
			leaderboardEmbed = embeds[leaderboardType]
		else:
			leaderboardType = "messageLeaderboard"
			leaderboard = self.leaderboards[str(ctx.message.guild.id)]["messageLeaderboard"]
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

			if leaderboardType == "reactionLeaderboard":
				name = str(participant)
			elif leaderboardType == "emojiLeaderboard":
				for emoji in guild.emojis:
					if int(participant) == emoji.id:
						name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
						break
			else:
				name = "<@" + str(participant) + ">"
				# if int(participant) == 456226577798135808:
				# 	# Skip deleted users
				# 	True
				# elif guild.get_member(int(participant)) is None:
				# 	name = str(await self.bot.fetch_user(int(participant)))
				# else:
				# 	name = str(guild.get_member(int(participant)).display_name)

			userValues += "**" + str(position) + ". " + name + "** - " + str(score) + "\n\n\t"

		if userValues == "":
			userValues = "None"

		leaderboardEmbed.add_field(name="User", value="".join(userValues.split("\t")[0:10]), inline=True)

		message = await ctx.send(embed=leaderboardEmbed)
		self.cachedMessages[message.id] = {"type": leaderboardType, "page": 1}
		await message.add_reaction("⬅️")
		await message.add_reaction("➡️")

	@commands.command(pass_context=True, name="quotes")
	async def quotes(self, ctx):
		"""
		Sends the quotes leaderboard
		"""
		if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == 567179438047887381:
			await ctx.channel.trigger_typing()
			await self.message_leaderboard(ctx, "quotes")

	@commands.command(pass_context=True, name="messages")
	@commands.check(command_channels)
	async def messages(self, ctx):
		"""
		Sends the messages leaderboard
		"""
		await ctx.channel.trigger_typing()
		await self.message_leaderboard(ctx, "messages")

	@commands.command(pass_context=True, name="reactions")
	@commands.check(command_channels)
	async def reactions(self, ctx):
		"""
		Sends the reactions leaderboard
		"""
		await ctx.channel.trigger_typing()
		await self.message_leaderboard(ctx, "reactions")

	@commands.command(pass_context=True, name="emojis")
	@commands.check(command_channels)
	async def emojis(self, ctx):
		"""
		Sends the emoji leaderboard
		"""
		await ctx.channel.trigger_typing()
		await self.message_leaderboard(ctx, "emojis")

	@commands.command(pass_context=True, name="set")
	async def set_quote_channel(self, ctx):
		if ctx.message.author.guild_permissions.administrator:
			guild = ctx.message.guild

			for channel in ctx.message.channel_mentions:
				if self.leaderboards[str(guild.id)]["quotesChannel"] != str(channel.id):
					self.leaderboards[str(guild.id)]["quotesChannel"] = str(channel.id)

					print("Updating guild " + str(guild.id) + " to use quotes channel " + str(channel.id))

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
			self.leaderboards[str(guild.id)]["reactionLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["quoteLeaderboard"] = {}
			self.leaderboards[str(guild.id)]["emojiLeaderboard"] = {}

			for emoji in guild.emojis:
				self.leaderboards[str(guild.id)]["emojiLeaderboard"][str(emoji.id)] = 0

			await self.update_state()
			await self.update_leaderboards()
			print("Successfully reset leaderboards")

	async def score_leaderboard(self, guild, leaderboard, leaderboardType):
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

			if leaderboardType == "reactionLeaderboard":
				name = str(participant)
			elif leaderboardType == "emojiLeaderboard":
				for emoji in guild.emojis:
					if int(participant) == emoji.id:
						name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
						break
			else:
				name = "<@" + str(participant) + ">"
				# if guild.get_member(int(participant)) is None:
				# 	name = str(await self.bot.fetch_user(int(participant)))
				# else:
				# 	name = str(guild.get_member(int(participant)).display_name)

			userValues += "**" + str(position) + ". " + name + "** - " + str(score) + "\n\n\t"

		if userValues == "":
			userValues = "None"

		return userValues
