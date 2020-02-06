import json
import os
import discord
from discord.ext import commands

from Leaderboards import Leaderboards
from Settings import Settings


gompei = commands.Bot(command_prefix="%")

# Extensions
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Settings(gompei))

# Overwrite
gompei.remove_command("help")


@gompei.event
async def on_ready():

	await gompei.change_presence(activity=discord.Game(name="Underwater Hockey"))

	print("Logged on as {0}".format(gompei.user))


@gompei.command(pass_context=True)
async def help(ctx):
	helpEmbed = discord.Embed(title="Gompei Bot", colour=discord.Colour.red())
	helpEmbed.add_field(name="Commands", value="None yet you fucker")
	helpEmbed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
	helpEmbed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot")

	await ctx.message.channel.send(embed=helpEmbed)

gompei.run(json.load(open(os.path.join("config", "tokens.json")))["token"])