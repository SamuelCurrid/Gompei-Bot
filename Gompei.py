from GompeiFunctions import load_json, save_json
from Administration import Administration
from Permissions import command_channels, dm_commands
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


settings = {}
access_roles = [
    664719508404961293,
    567179738683015188,
    578350297978634240,
    578350427209203712,
    578350479688466455,
    692461531983511662,
    599319106478669844,
    638748298152509461,
    638748298152509461,
    630589807084699653,
    748941410639806554,
    634223378773049365
]
greetings = ["hello", "hi", "greetings", "howdy", "salutations", "hey", "oi", "dear", "yo ", "morning", "afternoon", "evening", "sup", "G'day", "good day"]
gompei_references = ["gompei", "672453835863883787", "goat"]
love_references = ["gompeiHug", "love", "ily", "<3", "❤"]
hate_references = ["fuck you", "sucks", "fucker", "idiot", "shithead", "eat shit", "hate"]
violent_references = ["kill", "murder", "attack", "skin", "ambush", "stab"]


async def update_guilds():
    """
    Updates guilds included in leaderboards.json
    """
    global settings

    saved_guilds = []
    for guild_id in settings:
        saved_guilds.append(int(guild_id))

    guilds = []
    for guild in gompei.guilds:
        guilds.append(guild.id)

    add_guilds = [x for x in guilds if x not in saved_guilds]
    remove_guilds = [x for x in saved_guilds if x not in guilds]

    # Add new guilds
    for guild_id in add_guilds:
        settings[str(guild_id)] = {"prefix": "."}

    # Remove disconnected guilds
    for guild_id in remove_guilds:
        settings.pop(str(guild_id))

    save_json(os.path.join("config", "settings.json"), settings)


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
    await gompei.process_commands(message)

    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot:
        message_embed = discord.Embed(description=message.content, timestamp=datetime.utcnow())
        message_embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
        message_embed.set_footer(text=message.author.id)
        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        attachments = []
        if len(message.attachments) > 0:
            for i in message.attachments:
                attachments.append(await i.to_file())

        if len(attachments) > 0:
            if len(message.content) > 0:
                message_embed.description = message.content + "\n\n**<File(s) Attached>**"
            else:
                message_embed.description = message.content + "**<File(s) Attached>**"
            await gompei_channel.send(embed=message_embed)
            await gompei_channel.send(files=attachments)
        else:
            await gompei_channel.send(embed=message_embed)
    else:
        if not message.author.bot:

            if any(x in message.content.lower() for x in gompei_references):
                if any(x in message.content.lower() for x in love_references):
                    await message.add_reaction("❤")
                elif any(x in message.content.lower() for x in hate_references):
                    await message.add_reaction("😢")
                elif any(x in message.content.lower() for x in greetings):
                    await message.add_reaction("👋")
                elif any(x in message.content.lower() for x in violent_references):
                    await message.add_reaction("😨")


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

        message_embed = discord.Embed(timestamp=datetime.utcnow())
        message_embed.colour = discord.Colour(0x8899d4)
        message_embed.set_author(name=after.author.name + "#" + before.author.discriminator, icon_url=after.author.avatar_url)
        message_embed.title = "Message edited by " + after.author.name + "#" + str(after.author.discriminator)
        message_embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
        message_embed.set_footer(text="ID: " + str(before.author.id))

        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        await gompei_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_edit(payload):
    # If the message is not cached
    if payload.cached_message is None:
        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)
        channel = wpi_discord.get_channel(payload.channel_id)

        # If not in the WPI discord
        if channel is None:
            message_embed = discord.Embed()
            message_embed.colour = discord.Colour(0x8899d4)
            message_embed.title = "Message edited by ???"
            message_embed.set_footer(text="Uncached message: " + str(payload.message_id))
            message_embed.timestamp = datetime.utcnow()

            await gompei_channel.send(embed=message_embed)


@gompei.event
async def on_message_delete(message):
    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot:
        message_embed = discord.Embed()
        message_embed.colour = discord.Colour(0xbe4041)
        message_embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
        message_embed.title = "Message deleted by " + message.author.name + "#" + str(message.author.discriminator)
        message_embed.description = message.content

        if len(message.attachments) > 0:  # Check for attachments
            for attachment in message.attachments:
                message_embed.add_field(name="Attachment", value=attachment.proxy_url)

        message_embed.set_footer(text="ID: " + str(message.author.id))
        message_embed.timestamp = datetime.utcnow()

        wpi_discord = gompei.get_guild(567169726250352640)
        gompei_channel = wpi_discord.get_channel(746002454180528219)

        await gompei_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_delete(payload):
    # If a DM message
    if not hasattr(payload, "guild_id"):
        # If the message is not cached
        if payload.cached_message is None:
            wpi_discord = gompei.get_guild(567169726250352640)
            gompei_channel = wpi_discord.get_channel(746002454180528219)

            message_embed = discord.Embed()
            message_embed.colour = discord.Colour(0xbe4041)
            message_embed.title = "Message deleted by ???"
            message_embed.set_footer(text="Uncached message: " + str(payload.message_id))
            message_embed.timestamp = datetime.utcnow()

            await gompei_channel.send(embed=message_embed)


@gompei.event
async def on_typing(channel, user, when):
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
        help_embed = discord.Embed(title="Gompei Bot", colour=discord.Colour.blue())
        help_embed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
        help_embed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
        help_embed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot/")

        await ctx.message.channel.send(embed=help_embed)


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
@commands.check(dm_commands)
async def lockout(ctx):
    guild = gompei.get_guild(567169726250352640)
    member = await guild.fetch_member(ctx.message.author.id)

    # Get lockout info
    with open(os.path.join("config", "lockout.json"), "r+") as lockout_file:
        lockout_info = json.loads(lockout_file.read())

    if str(member.id) in lockout_info:
        await ctx.send("You've already locked yourself out")
    else:
        # Get current roles
        role_ids = []
        for role in member.roles:
            role_ids.append(role.id)

        # Remove members roles (check if nitro booster)
        if member.premium_since is None:
            await member.edit(roles=[])
            role_ids.remove(620478981946212363)
        else:
            await member.edit(roles=[guild.get_role(620478981946212363)])

        # Store roles
        lockout_info[str(member.id)] = role_ids
        save_json(os.path.join("config", "lockout.json"), lockout_info)

        # DM User
        await member.send("Locked you out of the server. To get access back just type \".letmein\" here")


@gompei.command(pass_context=True, aliases=["letMeIn"])
@commands.check(dm_commands)
async def let_me_in(ctx):
    guild = gompei.get_guild(567169726250352640)
    member = await guild.fetch_member(ctx.message.author.id)

    # Get lockout info
    with open(os.path.join("config", "lockout.json"), "r+") as lockout_file:
        lockout_info = json.loads(lockout_file.read())

    if member is None:
        # Member is not in guild
        await ctx.send("You are not in the WPI Discord Server")
    else:
        if str(member.id) not in lockout_info:
            await ctx.send("You haven't locked yourself out")
        else:
            role_list = []
            for role_id in lockout_info[str(member.id)]:
                role_list.append(guild.get_role(role_id))

            await member.edit(roles=role_list)

            del lockout_info[str(member.id)]
            with open(os.path.join("config", "lockout.json"), "r+") as lockout_file:
                lockout_file.truncate(0)
                lockout_file.seek(0)
                json.dump(lockout_info, lockout_file, indent=4)

            await member.send("Welcome back to the server :)")


# Run the bot
gompei.run(sys.argv[1])
