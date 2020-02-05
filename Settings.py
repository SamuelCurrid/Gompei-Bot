import discord
from discord.ext import commands

import os
import json


class Settings(commands.Cog):
	def __init__(self, bot):
		self.settings = {}
