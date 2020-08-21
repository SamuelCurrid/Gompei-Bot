import json
import os
import sys

import discord
from discord.ext import commands

from Leaderboards import Leaderboards
from Administration import Administration
from MovieVoting import MovieVoting
from Hangman import Hangman
from Minesweeper import Minesweeper

from Logging import Logging
from Statistics import Statistics


# State handling
settings = {}


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


def get_prefix(client, message):
	if isinstance(message.channel, discord.DMChannel):
		return "."

	return settings[str(message.guild.id)]["prefix"]


# Initialize Bot
gompei = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

# Load Extensions
print("Loading cogs...")
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Administration(gompei))

if len(sys.argv) > 2:
	gompei.add_cog(MovieVoting(gompei, sys.argv[2]))
else:
	print("No OMDb token passed! Not loading MovieVoting")

gompei.add_cog(Hangman(gompei))
gompei.add_cog(Minesweeper(gompei))
gompei.add_cog(Statistics(gompei))
gompei.add_cog(Logging(gompei))
print("Cogs loaded")

# Overwrite help command
gompei.remove_command("help")


# Events
@gompei.event
async def on_ready():
	"""
	Load state and update information since last run
	"""
	await load_state()
	await gompei.change_presence(activity=discord.Game(name="Underwater Hockey"))
	await update_guilds(gompei)

	print("Logged on as {0}".format(gompei.user))

@gompei.event
async def on_message(message):
	"""
	Forwards DMs to a channel
	"""
	if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot:
		wpi_discord = gompei.get_guild(567169726250352640)
		gompei_channel = wpi_discord.get_channel(746002454180528219)

		attachments = []
		if len(message.attachments) > 0:
			for i in message.attachments:
				attachments.append(await i.to_file())

		if len(message.content) > 0:
			await gompei_channel.send(message.clean_content + "\n-<@" + str(message.author.id) + ">", files=attachments)
		elif len(attachments) > 0:
			await gompei_channel.send("<@" + str(message.author.id) + ">", files=attachments)

	await gompei.process_commands(message)



#Commands
@gompei.command(pass_context=True)
async def help(ctx):
	"""
	Sends help information
	"""
	if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == 567179438047887381:
		helpEmbed = discord.Embed(title="Gompei Bot", colour=discord.Colour.blue())
		helpEmbed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
		helpEmbed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
		helpEmbed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot/")

		await ctx.message.channel.send(embed=helpEmbed)


@gompei.command(pass_context=True, name="prefix")
async def change_prefix(ctx, prefix):
	if ctx.message.author.guild_permissions.administrator:
		settings[str(ctx.message.guild.id)]["prefix"] = str(prefix)

		await update_state()


@gompei.command()
async def ping(ctx):
	"""
	Sends bot latency
	"""
	if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == 567179438047887381:
		await ctx.send(f'Pong! `{int(gompei.latency * 1000)}ms`')

# Run the bot
gompei.run(sys.argv[1])
