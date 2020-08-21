from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from discord.ext import commands
from pytimeparse import parse
import asyncio


def administrator_perms(ctx):
	return ctx.message.author.guild_permissions.administrator


def moderator_perms(ctx):
	return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == 742118136458772551


def parse_id(arg):
	"""
	Parses an ID from a discord @
	:param arg: @ or ID passed
	:return: ID
	"""
	if "<" in arg:
		for i, c in enumerate(arg):
			if c.isdigit():
				return int(arg[i:-1])
	# Using ID
	else:
		return int(arg)


def timeDeltaString(date1, date2):
	"""
	Returns a string with three most significant time deltas between date1 and date2
	:param date1: datetime 1
	:param date2: datetime 2
	:return: string
	"""
	output = ""
	delta = relativedelta.relativedelta(date2, date1)

	if delta.years > 0:
		if delta.years == 1:
			output = str(delta.years) + " year, "
		else:
			output = str(delta.years) + " years, "
		if delta.months == 1:
			output += str(delta.months) + " month, "
		else:
			output += str(delta.months) + " months, "

		if delta.days == 1:
			output += "and " + str(delta.days) + " day"
		else:
			output += "and " + str(delta.days) + " days"

		return output

	elif delta.months > 0:
		if delta.months == 1:
			output = str(delta.months) + " month, "
		else:
			output = str(delta.months) + " months, "
		if delta.days == 1:
			output += str(delta.days) + " day, "
		else:
			output += str(delta.days) + " days, "
		if delta.hours == 1:
			output += "and " + str(delta.hours) + " hour"
		else:
			output += "and " + str(delta.hours) + " hours"

		return output

	elif delta.days > 0:
		if delta.days == 1:
			output = str(delta.days) + " day, "
		else:
			output = str(delta.days) + " days, "
		if delta.hours == 1:
			output += str(delta.hours) + " hour, "
		else:
			output += str(delta.hours) + " hours, "
		if delta.minutes == 1:
			output += "and " + str(delta.minutes) + " minute"
		else:
			output += "and " + str(delta.minutes) + " minutes"

		return output

	elif delta.hours > 0:
		if delta.hours == 1:
			output = str(delta.hours) + " hour, "
		else:
			output = str(delta.hours) + " hours, "
		if delta.minutes == 1:
			output += str(delta.minutes) + " minute, "
		else:
			output += str(delta.minutes) + " minutes, "
		if delta.seconds == 1:
			output += "and " + str(delta.seconds) + " second"
		else:
			output += "and " + str(delta.seconds) + " seconds"

		return output

	elif delta.minutes > 0:
		if delta.minutes == 1:
			output = str(delta.minutes) + " minute "
		else:
			output = str(delta.minutes) + " minutes "
		if delta.seconds == 1:
			output += "and " + str(delta.seconds) + " second"
		else:
			output += "and " + str(delta.seconds) + " seconds"

		return output

	elif delta.seconds > 0:
		if delta.seconds == 1:
			return str(delta.seconds) + " second"
		else:
			return str(delta.seconds) + " seconds"

	return "!!DATETIME ERROR!!"


class Administration(commands.Cog):
	"""
	Administration tools
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	@commands.check(administrator_perms)
	async def echo(self, ctx, arg1):
		"""
		Forwards given message / attachments to given channel
		"""
		channel = ctx.guild.get_channel(int(arg1[2:-1]))

		if channel is not None:
			attachments = []

			if len(ctx.message.attachments) > 0:
				for i in ctx.message.attachments:
					attachments.append(await i.to_file())

			message = ctx.message.content[7 + len(arg1):]
			if len(message) > 0:
				await channel.send(message, files=attachments)
			elif len(attachments) > 0:
				await channel.send(files=attachments)
			else:
				await ctx.send("No content to send.")
		else:
			await ctx.send("Not a valid channel")

	@echo.error
	async def echo_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			print("!ERROR! " + str(ctx.author.id) + " did not have permissions for echo command")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments")
		else:
			print(error)

	@commands.command(pass_context=True)
	@commands.check(administrator_perms)
	async def echoPM(self, ctx, arg1):
		"""
		Fowards given message / attachments to give user
		"""
		member = ctx.guild.get_member(parse_id(arg1))

		if member is None:
			await ctx.send("Not a valid member")
			return

		attachments = []
		if len(ctx.message.attachments) > 0:
			for i in ctx.message.attachments:
				attachments.append(await i.to_file())

		message = ctx.message.content[9 + len(arg1):]
		if len(message) > 0:
			await member.send(message, files=attachments)
		elif len(attachments) > 0:
			await member.send(files=attachments)
		else:
			await ctx.send("No content to send")

		await ctx.message.add_reaction("👍")

	@echoPM.error
	async def echoPM_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			print("!ERROR! " + str(ctx.author.id) + " did not have permissions for echo command")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments")
		else:
			print(error)

	@commands.command(pass_context=True)
	@commands.check(moderator_perms)
	async def purge(self, ctx, arg1):
		"""
		Purges a number of messages in channel used
		:param arg1: number of messages to purge
		"""
		await ctx.channel.purge(limit=int(arg1) + 1)

	@purge.error
	async def purge_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			print("!ERROR! " + str(ctx.author.id) + " did not have permissions for purge command")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments")
		else:
			print(error)

	@commands.command(pass_context=True, name="spurge")
	@commands.check(moderator_perms)
	async def selective_purge(self, ctx, arg1, arg2):
		"""
		Purges messages from a specific user in the channel
		:param arg1: user to purge
		:param arg2: number of messages to purge
		"""
		member = ctx.guild.get_member(parse_id(arg1))

		messages = [ctx.message]
		oldMessage = ctx.message
		count = 0

		while count < int(arg2):
			async for message in ctx.message.channel.history(limit=int(arg2), before=oldMessage, oldest_first=False):
				if message.author == member:
					count += 1
					messages.append(message)

					if count == int(arg2):
						break

				oldMessage = message.created_at

		await ctx.channel.delete_messages(messages)

	@selective_purge.error
	async def selective_purge_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			print("!ERROR! " + str(ctx.author.id) + " did not have permissions for selective purge command")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments")
		else:
			print(error)

	@commands.command(pass_context=True)
	@commands.check(moderator_perms)
	async def mute(self, ctx, arg1, arg2):
		member = ctx.guild.get_member(parse_id(arg1))
		mutedRole = ctx.guild.get_role(615956736616038432)

		# Is user already muted
		if mutedRole in member.roles:
			await ctx.send("This member is already muted")
			return

		# Check role hierarchy
		if ctx.author.top_role.position <= member.top_role.position:
			await ctx.send("You're not high enough in the role hierarchy to do that.")
			return

		username = member.name + "#" + str(member.discriminator)

		seconds = parse(arg2)
		if seconds is None:
			await ctx.send("Not a valid time, try again")

		delta = timedelta(seconds=seconds)
		reason = ctx.message.content[8 + len(arg1 + arg2):]
		if len(reason) < 1:
			await ctx.send("You must include a reason for the mute")
			return

		muteTime = timeDeltaString(datetime.utcnow(), datetime.utcnow() + delta)

		await member.add_roles(mutedRole)
		await ctx.send("**Muted** user **" + username + "** for **" + muteTime + "** for: **" + reason + "**")
		await member.send("**You were muted in the WPI Discord Server for " + muteTime + "\nReason:** " + reason)

		await asyncio.sleep(seconds)

		await member.remove_roles(mutedRole)
		await ctx.send("**Unmuted** user **" + username + "**")

	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments: .mute <user> <minutes> <reason>")
		if isinstance(error, commands.CommandInvokeError):
			await ctx.send("Invalid mute time")
