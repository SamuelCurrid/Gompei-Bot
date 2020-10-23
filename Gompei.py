from GompeiFunctions import load_json, save_json
from Administration import Administration
from Permissions import command_channels
from ReactionRoles import ReactionRoles
from Leaderboards import Leaderboards
from MovieVoting import MovieVoting
from Minesweeper import Minesweeper
from Statistics import Statistics
from discord.ext import commands
from datetime import datetime
from Hangman import Hangman
from Logging import Logging

import discord
import json
import os
import sys


# State handling
settings = {}
access_roles = [664719508404961293, 567179738683015188, 578350297978634240, 578350427209203712, 578350479688466455, 692461531983511662, 599319106478669844, 638748298152509461, 638748298152509461, 630589807084699653, 748941410639806554, 634223378773049365]


async def update_guilds():
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

    save_json(os.path.join("config", "settings.json"), settings)


def get_prefix(message):
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
gompei.add_cog(ReactionRoles(gompei))
print("Cogs loaded")

# Overwrite help command
gompei.remove_command("help")


# Events
@gompei.event
async def on_ready():
    """
    Load state and update information since last run
    """
    global settings

    settings = load_json(os.path.join("config", "settings.json"))
    await gompei.change_presence(activity=discord.Game(name="Underwater Hockey"))
    await update_guilds()

    print("Logged on as {0}".format(gompei.user))


@gompei.event
async def on_message(message):
    """
    Forwards DMs to a channel
    """
    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot:
        messageEmbed = discord.Embed(description=message.content, timestamp=datetime.utcnow())
        messageEmbed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
        messageEmbed.set_footer(text=message.author.id)
        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        attachments = []
        if len(message.attachments) > 0:
            for i in message.attachments:
                attachments.append(await i.to_file())

        if len(attachments) > 0:
            if len(message.content) > 0:
                messageEmbed.description = message.content + "\n\n**<File(s) Attached>**"
            else:
                messageEmbed.description = message.content + "**<File(s) Attached>**"
            await gompei_channel.send(embed=messageEmbed)
            await gompei_channel.send(files=attachments)
        else:
            await gompei_channel.send(embed=messageEmbed)
    else:
        if not message.author.bot:
            if "769305840112762950" in message.content:
                await message.add_reaction("❤")
            if "gompei" in message.content.lower() or "672453835863883787" in message.content.lower():
                await message.add_reaction("👋")

    await gompei.process_commands(message)


@gompei.event
async def on_message_edit(before, after):
    """
    Forwards messages edited in DMs to a channel
    :param before:
    :param after:
    :return:
    """
    if isinstance(before.channel, discord.channel.DMChannel) and not before.author.bot:
        if before.content is after.content:
            return

        messageEmbed = discord.Embed(timestamp=datetime.utcnow())
        messageEmbed.colour = discord.Colour(0x8899d4)
        messageEmbed.set_author(name=after.author.name + "#" + before.author.discriminator, icon_url=after.author.avatar_url)
        messageEmbed.title = "Message edited by " + after.author.name + "#" + str(after.author.discriminator)
        messageEmbed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
        messageEmbed.set_footer(text="ID: " + str(before.author.id))

        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        await gompei_channel.send(embed=messageEmbed)


@gompei.event
async def on_message_delete(message):
    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot:
        messageEmbed = discord.Embed()
        messageEmbed.colour = discord.Colour(0xbe4041)
        messageEmbed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
        messageEmbed.title = "Message deleted by " + message.author.name + "#" + str(message.author.discriminator)
        messageEmbed.description = message.content

        if len(message.attachments) > 0:  # Check for attachments
            for attachment in message.attachments:
                messageEmbed.add_field(name="Attachment", value=attachment.proxy_url)

        messageEmbed.set_footer(text="ID: " + str(message.author.id))
        messageEmbed.timestamp = datetime.utcnow()

        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        await gompei_channel.send(embed=messageEmbed)


@gompei.event
async def on_typing(channel, user):
    if isinstance(channel, discord.channel.DMChannel) and not user.bot:
        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)
        await gompei_channel.trigger_typing()


@gompei.event
async def on_member_update(before, after):
    """
    Load state and update information since last run
    """
    if len(after.roles) < len(before.roles):
        role_list = []
        for role in after.roles:
            if role.id in access_roles:
                return
            if role.id != 725887796312801340:
                role_list.append(role)

        await after.edit(roles=role_list)


# Commands
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

        save_json(os.path.join("config", "settings.json"), settings)


@gompei.command()
async def ping(ctx):
    """
    Sends bot latency
    """
    if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == 567179438047887381:
        await ctx.send(f'Pong! `{int(gompei.latency * 1000)}ms`')


@gompei.command(pass_context=True)
@commands.check(command_channels)
async def lockout(ctx):
    guild = gompei.get_guild(567169726250352640)
    member = guild.get_member(ctx.message.author.id)

    # Get lockout info
    with open(os.path.join("config", "lockout.json"), "r+") as lockoutFile:
        lockoutInfo = json.loads(lockoutFile.read())

    if str(member.id) in lockoutInfo:
        await ctx.send("You've already locked yourself out")
    else:
        # Get current roles
        role_IDs = []
        for role in member.roles:
            role_IDs.append(role.id)

        # Store roles
        lockoutInfo[str(member.id)] = role_IDs
        with open(os.path.join("config", "lockout.json"), "r+") as lockoutFile:
            lockoutFile.truncate(0)
            lockoutFile.seek(0)
            json.dump(lockoutInfo, lockoutFile, indent=4)

        # Remove members roles
        await member.edit(roles=[])

        # DM User
        await member.send("Locked you out of the server. To get access back just type \".letmein\" here")


@gompei.command(pass_context=True)
@commands.check(command_channels)
async def letmein(ctx):
    guild = gompei.get_guild(567169726250352640)
    member = guild.get_member(ctx.message.author.id)

    # Get lockout info
    with open(os.path.join("config", "lockout.json"), "r+") as lockoutFile:
        lockoutInfo = json.loads(lockoutFile.read())

    if member is None:
        # Member is not in guild
        await ctx.send("You are not in the WPI Discord Server")
    else:
        if str(member.id) not in lockoutInfo:
            await ctx.send("You haven't locked yourself out")
        else:
            roleList = []
            for roleID in lockoutInfo[str(member.id)]:
                roleList.append(guild.get_role(roleID))

            await member.edit(roles=roleList)

            del lockoutInfo[str(member.id)]
            with open(os.path.join("config", "lockout.json"), "r+") as lockoutFile:
                lockoutFile.truncate(0)
                lockoutFile.seek(0)
                json.dump(lockoutInfo, lockoutFile, indent=4)

            await member.send("Welcome back to the server :)")


# Run the bot
gompei.run(sys.argv[1])
