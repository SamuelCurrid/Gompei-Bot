from Permissions import moderator_perms
from discord.ext import commands

import discord
import json
import os


class ReactionRoles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.reaction_messages = {}
		self.load_reaction_messages()

	def load_reaction_messages(self):
		try:
			with open(os.path.join("config", "reactionMessages.json"), "r+") as reaction_messages_file:
				self.reaction_messages = json.loads(reaction_messages_file.read())
		except (OSError, IOError):
			with open(os.path.join("config", "reactionMessages.json"), "r+") as reaction_messages_file:
				reaction_messages_file.truncate(0)
				reaction_messages_file.seek(0)
				json.dump(self.reaction_messages, reaction_messages_file, indent=4)

	def save_reaction_messages(self):
		with open(os.path.join("config", "reactionMessages.json"), "r+") as reaction_messages_file:
			reaction_messages_file.truncate(0)
			reaction_messages_file.seek(0)
			json.dump(self.reaction_messages, reaction_messages_file, indent=4)

	@commands.check(moderator_perms)
	@commands.command(pass_context=True, aliases=['rradd'])
	async def add_reaction_role(self, ctx, message_link, role_id, emoji):
		messageID = int(message_link[message_link.rfind("/") + 1:])
		shortLink = message_link[:message_link.rfind("/")]
		channelID = int(shortLink[shortLink.rfind("/") + 1:])

		channel = ctx.guild.get_channel(channelID)
		if channel is None:
			await ctx.send("Not a valid link to message")
		else:
			message = await channel.fetch_message(messageID)
			if message is None:
				await ctx.send("Not a valid link to message")
			else:
				role = ctx.guild.get_role(int(role_id))

				if role is None:
					await ctx.send("Not a valid role ID")
				else:
					if ctx.message.author.top_role.position < role.position:
						await ctx.send("You do not have permission to make a reaction role for this role")
					else:
						await message.add_reaction(emoji)

						# Get a list of pre-existing reactions
						reactions = [self.bot.user.id]
						for reaction in message.reactions:
							if type(reaction.emoji) is discord.Emoji:
								emoji_name = "<:" + reaction.emoji.name + ":" + str(reaction.emoji.id) + ">"
							else:
								emoji_name = reaction.emoji

							print(emoji_name + " vs. " + emoji)
							if emoji_name == emoji:
								print("got here")

								async for user in reaction.users():
									reactions.append(user.id)
								break

						combinedID = str(channelID) + str(messageID)

						if combinedID in self.reaction_messages:
							self.reaction_messages[combinedID][emoji] = {"id": role_id, "users": reactions}
						else:
							self.reaction_messages[combinedID] = {emoji: {"id": role_id, "users": reactions}}

						self.save_reaction_messages()
						await ctx.send("Created reaction role")

	@commands.check(moderator_perms)
	@commands.command(pass_context=True, aliases=['rrdelete', 'rremove'])
	async def remove_reaction_role(self, ctx, message_link, emoji):
		messageID = int(message_link[message_link.rfind("/") + 1:])
		shortLink = message_link[:message_link.rfind("/")]
		channelID = int(shortLink[shortLink.rfind("/") + 1:])

		key = str(channelID) + str(messageID)
		if key not in self.reaction_messages:
			await ctx.send("There are no reaction roles on this message")
		else:
			if emoji not in self.reaction_messages[key]:
				await ctx.send("This emoji is not used on this reaction role")
			else:
				del self.reaction_messages[key][emoji]
				self.save_reaction_messages()
				channel = ctx.guild.get_channel(channelID)
				message = await channel.fetch_message(messageID)

				await message.remove_reaction(emoji, self.bot.user)
				await ctx.send("Removed reaction role")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if not payload.member.bot:
			key = str(payload.channel_id) + str(payload.message_id)
			if key in self.reaction_messages:
				if str(payload.emoji) in self.reaction_messages[key]:
					role_id = self.reaction_messages[key][str(payload.emoji)]["id"]
					guild = self.bot.get_guild(567169726250352640)
					role = guild.get_role(int(role_id))
					member = payload.member
					roles = member.roles
					roles.append(role)

					self.reaction_messages[key][str(payload.emoji)]["users"].append(member.id)
					self.save_reaction_messages()

					await payload.member.edit(roles=roles)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		key = str(payload.channel_id) + str(payload.message_id)
		if key in self.reaction_messages:
			if str(payload.emoji) in self.reaction_messages[key]:
				role_id = self.reaction_messages[key][str(payload.emoji)]["id"]
				guild = self.bot.get_guild(567169726250352640)
				role = guild.get_role(int(role_id))

				channel = guild.get_channel(int(key[0:18]))
				message = await channel.fetch_message(int(key[18:]))

				for reaction in message.reactions:
					if type(reaction.emoji) is discord.Emoji:
						emoji_name = "<:" + reaction.emoji.name + ":" + str(reaction.emoji.id) + ">"

					else:
						emoji_name = reaction.emoji

					if emoji_name == str(payload.emoji):

						for user in self.reaction_messages[key][str(payload.emoji)]["users"]:
							found = False
							async for reacted in reaction.users():
								if user == reacted.id:
									found = True
									break

							if not found:
								member = guild.get_member(user)
								self.reaction_messages[key][str(payload.emoji)]["users"].remove(user)
								if member is not None:
									await member.remove_roles(role)
