from discord.ext import commands
import asyncio


def module_perms(ctx):
	return ctx.message.author.guild_permissions.administrator


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


class Administration(commands.Cog):
	"""
	Administration tools
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	@commands.check(module_perms)
	async def echo(self, ctx, arg1):
		"""
		Forwards given message / attachments to channel
		"""
		channel = ctx.guild.get_channel(int(arg1[2:-1]))

		if channel is not None:
			images = []

			if len(ctx.message.attachments) > 0:
				for i in ctx.message.attachments:
					images.append(await i.to_file())

			message = ctx.message.content[7 + len(arg1):]
			if len(message) > 0:
				await channel.send(message, files=images)
			elif len(images) > 0:
				await channel.send(files=images)
			else:
				await ctx.send("No content to send.")

	@echo.error
	async def echo_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			print("!ERROR! " + str(ctx.author.id) + " did not have permissions for echo command")
		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments")
		else:
			print(error)

	@commands.command(pass_context=True)
	@commands.check(module_perms)
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
	@commands.check(module_perms)
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
	@commands.check(module_perms)
	async def mute(self, ctx, arg1, arg2):
		member = ctx.guild.get_member(parse_id(arg1))
		username = member.name + "#" + str(member.discriminator)
		minutes = int(arg2)
		reason = ctx.message.content[8 + len(arg1 + arg2):]

		mutedRole = ctx.guild.get_role(615956736616038432)

		await member.add_roles(mutedRole)
		await ctx.send("**Muted** user **" + username + "** for **" + str(minutes) + " minutes** for: **" + reason + "**")
		await member.send("**You were muted in the WPI Discord Server for:** " + reason)

		await asyncio.sleep(60 * minutes)

		await member.remove_roles(mutedRole)
		await ctx.send("**Unmuted** user **" + username + "**")

	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("Command is missing arguments: .mute <user> <minutes> <reason>")
		if isinstance(error, commands.CommandInvokeError):
			await ctx.send("Invalid mute time")





