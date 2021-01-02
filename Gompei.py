# Utility
from cogs.Permissions import dm_commands, administrator_perms, owner
from GompeiFunctions import time_delta_string
from config import Config

# Cogs
from cogs.Administration import Administration
from cogs.DirectMessages import DirectMessages
from cogs.ReactionRoles import ReactionRoles
from cogs.Leaderboards import Leaderboards
from cogs.Information import Information
from cogs.Logging import Logging
from cogs.Voting import Voting
from cogs.Games import Games
from cogs.Roles import Roles

# Libraries
from discord.ext import commands
from datetime import datetime
import discord
import sys


def get_prefix(client, message):
    return Config.prefix


# Initialize Bot
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guilds = True
gompei = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

# Load Extensions
print("Loading cogs...")
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Administration(gompei))
gompei.add_cog(DirectMessages(gompei))

# if len(sys.argv) > 2:
#     gompei.add_cog(MovieVoting(gompei, sys.argv[2]))
# else:
#     print("No OMDb token passed! Not loading MovieVoting")

gompei.add_cog(Games(gompei))
gompei.add_cog(Information(gompei))
gompei.add_cog(Logging(gompei))
gompei.add_cog(ReactionRoles(gompei))
gompei.add_cog(Voting(gompei))
gompei.add_cog(Roles(gompei))
print("Cogs loaded")

# Overwrite help command
gompei.remove_command("help")


# Events
@gompei.event
async def on_ready():
    """
    Load state and update information since last run
    """
    if Config.status is not None:
        await gompei.change_presence(activity=discord.Game(name=Config.status, start=datetime.utcnow()))

    await Config.set_client(gompei)
    await Config.load_settings()

    print("Logged on as {0}".format(gompei.user))
    if Config.dm_channel is not None:
        start_embed = discord.Embed(title="Bot started", color=0x43b581)
        start_embed.set_author(name=gompei.user.name + "#" + gompei.user.discriminator, icon_url=gompei.user.avatar_url)
        if Config.close_time is None:
            start_embed.description = "**Downtime:** NaN"
        else:
            start_embed.description = "**Downtime:** " + time_delta_string(Config.close_time, datetime.now())

        start_embed.set_footer(text="ID: " + str(gompei.user.id))
        start_embed.timestamp = datetime.utcnow()

        await Config.dm_channel.send(embed=start_embed)

    Config.clear_close_time()


@gompei.event
async def on_command_error(ctx, error):
    """
    Default error handling for the bot

    :param ctx: context object
    :param error: error
    """
    if isinstance(error, commands.CheckFailure):
        print("!ERROR! " + str(ctx.author.id) + " did not have permissions for " + ctx.command.name + " command")
    elif isinstance(error, commands.BadArgument):
        argument = list(ctx.command.clean_params)[len(ctx.args[2:] if ctx.command.cog else ctx.args[1:])]
        await ctx.send("Could not find the " + argument)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(ctx.command.name + " is missing arguments")
    else:
        print(error)


# Commands
@gompei.command(pass_context=True)
@commands.check(administrator_perms)
async def kill(ctx):
    """
    Clean shutdown for the bot

    :param ctx: Context object
    """

    def check_author(message):
        return message.author.id == ctx.author.id

    query = await ctx.send("You are about to shut down the bot, are you sure you want to do this? (Y/N)")

    response = await gompei.wait_for('message', check=check_author)

    if response.content.lower() == "y" or response.content.lower() == "yes":
        Config.set_close_time()
        if Config.dm_channel is not None:
            end_embed = discord.Embed(title="Bot shutting down", color=0xbe4041)
            end_embed.set_author(name=gompei.user.name + "#" + gompei.user.discriminator, icon_url=gompei.user.avatar_url)
            end_embed.set_footer(text="ID: " + str(gompei.user.id))
            end_embed.timestamp = datetime.utcnow()

            await Config.dm_channel.send(embed=end_embed)
        await gompei.close()
    else:
        await ctx.send("Not shutting down the bot")


@gompei.command(pass_context=True)
@commands.check(dm_commands)
async def help(ctx, command_name=None):
    """
    Sends help information
    Usage: .help (command)

    :param ctx: context object
    :param command_name: command in question
    """
    if command_name is None:
        help_embed = discord.Embed(title=gompei.user.display_name, colour=discord.Colour.blue())
        help_embed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
        help_embed.set_thumbnail(url=gompei.user.avatar_url)
        help_embed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot/")
        await ctx.send(embed=help_embed)
    else:
        command = gompei.get_command(command_name)
        if command is None:
            await ctx.send("Could not find the command " + command_name)
        else:
            description = command.help[:command.help.find("Usage:") - 1]
            usage = command.help[command.help.find("Usage:") + 7:command.help.find("\n\n")]
            embed = discord.Embed(title=command.name, colour=discord.Colour.blue())
            embed.description = description + "\n\n**Usage:** `" + usage + "`\n\n**Aliases:** " + ", ".join(command.aliases)
            embed.set_footer(text="<> = required, () = optional")
            await ctx.send(embed=embed)


@gompei.command(pass_context=True, name="prefix")
@commands.check(administrator_perms)
async def change_prefix(ctx, prefix):
    """
    Changes the bots prefix
    Usage: .prefix <prefix>

    :param ctx: context object
    :param prefix: prefix to change to
    """
    if " " in prefix:
        await ctx.send("Not a valid prefix")
    else:
        Config.set_prefix(prefix)
        await ctx.send("Update prefix to `" + str(prefix) + "`")


@gompei.command()
@commands.check(dm_commands)
async def ping(ctx):
    """
    Sends bot latency
    Usage: .ping

    :param ctx: context object
    """
    await ctx.send(f'Pong! `{int(gompei.latency * 1000)}ms`')


@gompei.command(pass_context=True, aliases=["status"])
@commands.check(administrator_perms)
@commands.guild_only()
async def set_status(ctx, *, status: str):
    """
    Set the bots status ("Now playing <insert>")
    Usage: .status <status>

    :param ctx: context object
    :param status: status
    """
    if len(status) > 128:
        await ctx.send("This status is too long! (128 character limit)")
    else:
        Config.set_status(status)
        await ctx.send("Successfully updated status")


@gompei.command(pass_context=True, name="setGuild")
@commands.guild_only()
@commands.is_owner()
async def set_guild(ctx):
    """
    Sets the guild for the bot

    :param ctx: Context object
    """
    await Config.set_guild(ctx.guild)
    await ctx.send("Successfully set guild")


@gompei.command(pass_context=True, name="addCommandChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def add_command_channel(ctx, channel: discord.TextChannel):
    if channel not in Config.command_channels:
        Config.add_command_channel(channel)
        await ctx.send("Successfully added " + channel.mention + " as a command channel")
    else:
        await ctx.send("This is already a command channel")


@gompei.command(pass_context=True, name="removeCommandChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_command_channel(ctx, channel: discord.TextChannel):
    if channel in Config.command_channels:
        Config.remove_command_channel(channel)
        await ctx.send("Successfully removed " + channel.mention + " as a command channel")
    else:
        await ctx.send("Cannot remove a channel that is not already a command channel")


# Run the bot
gompei.run(sys.argv[1])
