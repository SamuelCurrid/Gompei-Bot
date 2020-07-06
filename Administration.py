from discord.ext import commands
from datetime import datetime


def module_perms(ctx):
	return ctx.message.author.guild_permissions.administrator


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
		if "<" in arg1:
			member = ctx.guild.get_member(int(arg1[3:-1]))
		else:
			member = ctx.guild.get_member(int(arg1))

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


	# @selective_purge.error
	# async def selective_purge_error(self, ctx, error):
	# 	if isinstance(error, commands.CheckFailure):
	# 		print("!ERROR! " + str(ctx.author.id) + " did not have permissions for selective purge command")
	# 	elif isinstance(error, commands.MissingRequiredArgument):
	# 		await ctx.send("Command is missing arguments")
	# 	else:
	# 		print(error)
