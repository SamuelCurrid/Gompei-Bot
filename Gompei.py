import json
import os
import discord
from discord.ext import commands

from Leaderboards import Leaderboards
from Administration import Administration

settings = {}


def get_prefix(client, message):
	return settings[str(message.guild.id)]["prefix"]


gompei = commands.Bot(command_prefix=get_prefix)

# Extensions
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Administration(gompei))

# Overwrite
gompei.remove_command("help")


@gompei.event
async def on_ready():
	"""
	Load state and update information since last run
	"""
	await load_state()
	await gompei.change_presence(activity=discord.Game(name="Underwater Hockey"))
	await update_guilds(gompei)

	print("Logged on as {0}".format(gompei.user))


async def load_state():
	global settings

	with open(os.path.join("config", "settings.json"), "r+") as settingsFile:
		settings = json.loads(settingsFile.read())


async def update_state():
	global settings

	with open(os.path.join("config", "settings.json"), "r+") as settingsFile:
		settingsFile.truncate(0)
		settingsFile.seek(0)
		json.dump(settings, settingsFile, indent=4)


@gompei.command(pass_context=True)
async def help(ctx):
	"""
	Sends help information
	"""

	helpEmbed = discord.Embed(title="Gompei Bot", colour=discord.Colour.red())
	helpEmbed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
	helpEmbed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
	helpEmbed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot/")

	await ctx.message.channel.send(embed=helpEmbed)


async def update_guilds(self):
	"""
	Updates guilds included in leaderboards.json
	"""
	global settings

	savedGuilds = []
	for guildID in settings:
		savedGuilds.append(int(guildID))

	guilds = []
	for guild in gompei.guilds:
		guilds.append(guild.id)

	addGuilds = [x for x in guilds if x not in savedGuilds]
	removeGuilds = [x for x in savedGuilds if x not in guilds]

	# Add new guilds
	for guildID in addGuilds:
		settings[str(guildID)] = {"prefix": "."}

	# Remove disconnected guilds
	for guildID in removeGuilds:
		settings.pop(str(guildID))

	await update_state()


@gompei.command(pass_context=True, name="prefix")
async def change_prefix(ctx, prefix):
	if ctx.message.author.guild_permissions.administrator:
		settings[str(ctx.message.guild.id)]["prefix"] = str(prefix)

		await update_state()




gompei.run(json.load(open(os.path.join("config", "tokens.json")))["token"])
