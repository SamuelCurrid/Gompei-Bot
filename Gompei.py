# Utility
from cogs.Permissions import dm_commands, administrator_perms
from GompeiFunctions import time_delta_string, yes_no_helper
from config import Config

# Libraries
from discord.ext import commands
from datetime import datetime

import traceback
import discord
import sys


def get_prefix(client, message):
    if message.guild is None:
        return Config.prefix

    guild_prefix = Config.guilds[message.guild]["prefix"]

    if guild_prefix is None:
        return Config.prefix
    else:
        return guild_prefix


# Initialize Bot
start_time = None
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guilds = True
gompei = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

# Overwrite help command
gompei.remove_command("help")


# Events
@gompei.event
async def on_ready():
    """
    Load state and update information since last run
    """
    global start_time

    if Config.status is not None:
        await gompei.change_presence(activity=discord.Game(name=Config.status, start=datetime.utcnow()))

    await Config.set_client(gompei)
    await Config.load_settings()

    start_time = datetime.utcnow()
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

    startup_cogs = [
        "Administration",
        "DirectMessages",
        "EmbedBuilder",
        "Games",
        "Highlights",
        "Information",
        "Leaderboards",
        "Logging",
        "Memes",
        "ReactionRoles",
        "Roles",
        "Triggers",
        "Verification",
        "Voting",
        "BotTools"
    ]

    for cog in startup_cogs:
        gompei.load_extension(f"cogs.{cog}")
        print(f"Loaded cog {cog}")

    Config.clear_close_time()


@gompei.event
async def on_command_error(ctx, error):
    """
    Default error handling for the bot

    :param ctx: context object
    :param error: error
    """
    if isinstance(error, commands.CheckFailure) or isinstance(error, commands.MissingPermissions):
        print("!ERROR! " + str(ctx.author.id) + " did not have permissions for " + ctx.command.name + " command")
    elif isinstance(error, commands.BadArgument):
        argument = list(ctx.command.clean_params)[len(ctx.args[2:] if ctx.command.cog else ctx.args[1:])]
        await ctx.send("Could not find the " + argument)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(ctx.command.name + " is missing arguments")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Bot is missing permissions.")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@gompei.event
async def on_guild_join(guild):
    Config.add_guild(guild)


@gompei.event
async def on_remove_join(guild):
    Config.add_guild(guild)


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

    await ctx.send("You are about to shut down the bot, are you sure you want to do this? (Y/N)")

    if await yes_no_helper(gompei, ctx):
        Config.set_close_time()
        if Config.dm_channel is not None:
            end_embed = discord.Embed(title="Bot shutting down", color=0xbe4041)
            end_embed.set_author(name=gompei.user.name + "#" + gompei.user.discriminator,
                                 icon_url=gompei.user.avatar_url)
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
            embed = discord.Embed(
                title=command.name,
                colour=discord.Colour.blue(),
                description=description + "\n\n**Usage:** `" + usage + "`\n\n**Aliases:** " + ", ".join(command.aliases)
            )

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
        Config.set_guild_prefix(ctx.guild, prefix)
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


@gompei.command()
@commands.check(dm_commands)
async def uptime(ctx):
    """
    Sends the bots uptime
    Usage: .uptime

    :param ctx: Context object
    """
    global start_time

    await ctx.send(f"{time_delta_string(start_time, datetime.utcnow())}")


@gompei.command(pass_context=True, aliases=["status"])
@commands.is_owner()
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
    await Config.set_main_guild(ctx.guild)
    await ctx.send("Successfully set guild")


@gompei.command(pass_context=True, name="addAnnouncementChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def add_announcement_channel(ctx, channel: discord.TextChannel):
    if channel not in Config.guilds[channel.guild]["announcement_channels"]:
        Config.add_announcement_channel(channel)
        await ctx.send("Successfully added " + channel.mention + " as an announcement channel")
    else:
        await ctx.send("This is already an announcement channel")


@gompei.command(pass_context=True, name="removeAnnouncementChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_announcement_channel(ctx, channel: discord.TextChannel):
    if channel in Config.guilds[channel.guild]["announcement_channels"]:
        Config.remove_announcement_channel(channel)
        await ctx.send("Successfully removed " + channel.mention + " as an announcement channel")
    else:
        await ctx.send("Cannot remove a channel that is not already an announcement channel")


@gompei.command(pass_context=True, name="addCommandChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def add_command_channel(ctx, channel: discord.TextChannel):
    if channel not in Config.guilds[channel.guild]["command_channels"]:
        Config.add_command_channel(channel)
        await ctx.send("Successfully added " + channel.mention + " as a command channel")
    else:
        await ctx.send("This is already a command channel")


@gompei.command(pass_context=True, name="removeCommandChannel")
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_command_channel(ctx, channel: discord.TextChannel):
    if channel in Config.guilds[channel.guild]["command_channels"]:
        Config.remove_command_channel(channel)
        await ctx.send("Successfully removed " + channel.mention + " as a command channel")
    else:
        await ctx.send("Cannot remove a channel that is not already a command channel")


# Run the bot
gompei.run(sys.argv[1])
