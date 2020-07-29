from discord.ext import commands


class Statistics(commands.Cog):
	"""
	Stat collection tools
	"""

	def __init__(self, bot):
		self.bot = bot


class GuildStats:

	def __init__(self):
		self.members = {}


class MemberStats:

	def __init__(self):
		self.messages = {}
