import json
import os
import discord
from discord.ext import commands

from Leaderboards import Leaderboards
from Settings import Settings
from AudioPlayer import AudioPlayer


gompei = commands.Bot(command_prefix=".")

# Extensions
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Settings(gompei))
gompei.add_cog(AudioPlayer(gompei))

# Overwrite
gompei.remove_command("help")


@gompei.event
async def on_ready():

	await gompei.change_presence(activity=discord.Game(name="Underwater Hockey"))
	await update_guilds(gompei)

	print("Logged on as {0}".format(gompei.user))


@gompei.command(pass_context=True)
async def help(ctx):
	helpEmbed = discord.Embed(title="Gompei Bot", colour=discord.Colour.red())
	helpEmbed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/")
	helpEmbed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
	helpEmbed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot")

	await ctx.message.channel.send(embed=helpEmbed)


async def update_guilds(self):
	"""
	Updates guilds included in leaderboards.json
	"""
	# with open(os.path.join("config", "settings"), "r+") as leaderboards:
	# 	guilds = json.loads(leaderboards.read())
	#
	# 	savedGuilds = []
	# 	for guildID in guilds:
	# 		savedGuilds.append(int(guildID))
	#
	# 	guilds = []
	# 	for guild in gompei.guilds:
	# 		guilds.append(guild.id)
	#
	# 	addGuilds = [x for x in guilds if x not in savedGuilds]
	# 	removeGuilds = [x for x in savedGuilds if x not in guilds]
	#
	# 	# Add new guilds
	# 	for guildID in addGuilds:
	# 		self.leaderboards[str(guildID)] = {"prefix": "."}

	# Remove disconnected guilds
	# for guildID in removeGuilds:
	# 	self.leaderboards.pop(str(guildID))
	return

gompei.run(json.load(open(os.path.join("config", "tokens.json")))["token"])