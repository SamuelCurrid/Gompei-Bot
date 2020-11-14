from GompeiFunctions import load_json, save_json, parse_id
from Administration import Administration
from Permissions import dm_commands, administrator_perms
from ReactionRoles import ReactionRoles
from Leaderboards import Leaderboards
from MovieVoting import MovieVoting
from Minesweeper import Minesweeper
from discord.ext import commands
from datetime import datetime
from Hangman import Hangman
from Logging import Logging
from Voting import Voting

import discord
import random
import json
import os
import sys


settings = {}

greetings = ["hello", "hi", "greetings", "howdy", "salutations", "hey", "oi", "dear", "yo ", "morning", "afternoon", "evening", "sup", "G'day", "good day", "bonjour"]
gompei_references = ["gompei", "672453835863883787", "goat"]
love_references = ["gompeiHug", "love", "ily", "<3", "❤"]
hate_references = ["fuck you", "sucks", "fucker", "idiot", "shithead", "eat shit", "hate"]
violent_references = ["kill", "murder", "attack", "skin", "ambush", "stab"]


def get_prefix(client, message):
    return settings["prefix"]


# Initialize Bot
intents = discord.Intents.default()
intents.members = True
gompei = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

# Load Extensions
print("Loading cogs...")
gompei.add_cog(Leaderboards(gompei))
gompei.add_cog(Administration(gompei))

# if len(sys.argv) > 2:
#     gompei.add_cog(MovieVoting(gompei, sys.argv[2]))
# else:
#     print("No OMDb token passed! Not loading MovieVoting")

gompei.add_cog(Hangman(gompei))
gompei.add_cog(Minesweeper(gompei))
gompei.add_cog(Logging(gompei))
gompei.add_cog(ReactionRoles(gompei))
gompei.add_cog(Voting(gompei))
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

    # Load the settings
    settings = load_json(os.path.join("config", "settings.json"))
    if settings["status"] is not None:
        await gompei.change_presence(activity=discord.Game(name=settings["status"], start=datetime.utcnow()))

    # Update the nitro booster role id for the guild; check if access / opt-in roles still exist
    if settings["guild_id"] is not None:
        guild = gompei.get_guild(settings["guild_id"])
        for role in guild.roles:
            if role.name == "Nitro Booster":
                if settings["nitro_booster_id"] != role.id:
                    settings["nitro_booster_id"] = role.id

        for role_id in settings["opt_in_roles"]:
            if guild.get_role(role_id) is None:
                del role_id

        for role_id in settings["access_roles"]:
            if guild.get_role(role_id) is None:
                del role_id

    print("Logged on as {0}".format(gompei.user))


@gompei.event
async def on_message(message):
    """
    Forwards DMs to a channel
    """
    if not message.author.bot:
        await gompei.process_commands(message)

        if message.author.id == 87585011070414848 and "beep beep" in message.content.lower():
            await message.channel.send("https://i.pinimg.com/originals/84/ee/27/84ee27382f9f9819097b29fe78be814d.png")

        if isinstance(message.channel, discord.channel.DMChannel) and settings["dm_channel_id"] is not None:
            message_embed = discord.Embed(description=message.content, timestamp=datetime.utcnow())
            message_embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
            message_embed.set_footer(text=message.author.id)
            guild = gompei.get_guild(settings["guild_id"])
            dm_channel = guild.get_channel(settings["dm_channel_id"])

            attachments = []
            if len(message.attachments) > 0:
                for i in message.attachments:
                    attachments.append(await i.to_file())

            if len(attachments) > 0:
                if len(message.content) > 0:
                    message_embed.description = message.content + "\n\n**<File(s) Attached>**"
                else:
                    message_embed.description = message.content + "**<File(s) Attached>**"

                message_embed.timestamp = datetime.utcnow()
                await dm_channel.send(embed=message_embed)
                await dm_channel.send(files=attachments)
            else:
                await dm_channel.send(embed=message_embed)
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
    if isinstance(before.channel, discord.channel.DMChannel) and not before.author.bot and settings["dm_channel_id"] is not None:
        if before.content is after.content:
            return

        message_embed = discord.Embed(timestamp=datetime.utcnow())
        message_embed.colour = discord.Colour(0x8899d4)
        message_embed.set_author(name=after.author.name + "#" + before.author.discriminator, icon_url=after.author.avatar_url)
        message_embed.title = "Message edited by " + after.author.name + "#" + str(after.author.discriminator)
        message_embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
        message_embed.set_footer(text="ID: " + str(before.author.id))
        message_embed.timestamp = datetime.utcnow()

        guild = gompei.get_guild(settings["guild_id"])
        dm_channel = guild.get_channel(settings["dm_channel_id"])

        await dm_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_edit(payload):
    # If the message is not cached
    if payload.cached_message is None:
        guild = gompei.get_guild(settings["guild_id"])
        dm_channel = guild.get_channel(settings["dm_channel_id"])
        channel = guild.get_channel(payload.channel_id)

        # If not in the guild
        if channel is None:
            message_embed = discord.Embed()
            message_embed.colour = discord.Colour(0x8899d4)
            message_embed.title = "Message edited by ???"
            message_embed.set_footer(text="Uncached message: " + str(payload.message_id))
            message_embed.timestamp = datetime.utcnow()

            await dm_channel.send(embed=message_embed)


@gompei.event
async def on_message_delete(message):
    # If a DM message
    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot and settings["dm_channel_id"] is not None:
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

        guild = gompei.get_guild(settings["guild_id"])
        dm_channel = guild.get_channel(settings["dm_channel_id"])

        await dm_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_delete(payload):
    # If a DM message
    if not hasattr(payload, "guild_id") and settings["dm_channel_id"] is not None:
        # If the message is not cached
        if payload.cached_message is None:
            guild = gompei.get_guild(settings["guild_id"])
            dm_channel = guild.get_channel(settings["dm_channel_id"])

            message_embed = discord.Embed()
            message_embed.colour = discord.Colour(0xbe4041)
            message_embed.title = "Message deleted by ???"
            message_embed.set_footer(text="Uncached message: " + str(payload.message_id))
            message_embed.timestamp = datetime.utcnow()

            await dm_channel.send(embed=message_embed)


@gompei.event
async def on_typing(channel, user, when):
    if isinstance(channel, discord.channel.DMChannel) and not user.bot and settings["dm_channel_id"] is not None:
        guild = gompei.get_guild(settings["guild_id"])
        dm_channel = guild.get_channel(settings["dm_channel_id"])
        await dm_channel.trigger_typing()


@gompei.event
async def on_member_update(before, after):
    """
    Removes opt in channel roles if losing access role
    """
    # Role checks
    added_roles = [x for x in after.roles if x not in before.roles]
    removed_roles = [x for x in before.roles if x not in after.roles]

    # If roles edited
    if len(added_roles) + len(removed_roles) > 0:
        role_list = []
        for role in after.roles:
            if role.id in settings["access_roles"]:
                return
            if role.id not in settings["opt_in_roles"]:
                role_list.append(role)

        await after.edit(roles=role_list)


@gompei.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        argument = list(ctx.command.clean_params)[len(ctx.args[2:] if ctx.command.cog else ctx.args[1:])]
        await ctx.send("Could not find the " + argument)
    elif isinstance(error, commands.CheckFailure):
        print("!ERROR! " + str(ctx.author.id) + " did not have permissions for " + ctx.command.name + " command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Command is missing arguments")
    else:
        print(error)


# Commands
@gompei.command(pass_context=True)
@commands.check(dm_commands)
async def help(ctx):
    """
    Sends help information
    Usage: .help

    :param ctx: context object
    """
    help_embed = discord.Embed(title="Gompei Bot", colour=discord.Colour.blue())
    help_embed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
    help_embed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
    help_embed.set_footer(text="Source: https://github.com/SamuelCurrid/Gompei-Bot/")

    await ctx.message.channel.send(embed=help_embed)


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
        settings["prefix"] = str(prefix)
        save_json(os.path.join("config", "settings.json"), settings)

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


@gompei.command(pass_context=True)
@commands.check(dm_commands)
async def lockout(ctx):
    """
    Removes user roles and stores them to be returned after
    Usage: .lockout

    :param ctx: context object
    """
    guild = gompei.get_guild(settings["guild_id"])
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
        else:
            await member.edit(roles=[guild.get_role(settings["nitro_booster_id"])])

        # Store roles
        lockout_info[str(member.id)] = role_ids
        save_json(os.path.join("config", "lockout.json"), lockout_info)

        # DM User
        await member.send("Locked you out of the server. To get access back just type \".letmein\" here")


@gompei.command(pass_context=True, aliases=["letMeIn"])
@commands.check(dm_commands)
async def let_me_in(ctx):
    """
    Returns user roles from a lockout command
    Usage: .letMeIn

    :param ctx: context object
    """
    guild = gompei.get_guild(settings["guild_id"])
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

                # Check if the role exists
                if guild.get_role(role_id) is not None:
                    role_list.append(guild.get_role(role_id))

            await member.edit(roles=role_list)

            del lockout_info[str(member.id)]
            with open(os.path.join("config", "lockout.json"), "r+") as lockout_file:
                lockout_file.truncate(0)
                lockout_file.seek(0)
                json.dump(lockout_info, lockout_file, indent=4)

            await member.send("Welcome back to the server :)")


@gompei.command(pass_context=True, aliases=["dmChannel"])
@commands.check(administrator_perms)
@commands.guild_only()
async def set_dm_channel(ctx, channel):
    """
    Sets the channel for DM events to be forwarded to
    Usage: .dmChannel <channel>

    :param ctx: context object
    :param channel: channel to set to
    """
    if ctx.guild.id != settings["guild_id"]:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    else:
        if channel.lower() == "clear":
            settings["dm_channel"] = None
            save_json(os.path.join("config", "settings.json"), settings)
            await ctx.send("Disabled the DM channel")
        else:
            channel_object = ctx.guild.get_channel(parse_id(channel))

            if channel_object is None:
                await ctx.send("Not a valid channel")
            elif channel_object.id == settings["dm_channel"]:
                await ctx.send("This is already the DM channel")
            else:
                settings["dm_channel"] = channel_object.id
                save_json(os.path.join("config", "settings.json"), settings)
                await ctx.send("Successfully updated DM channel to <#" + str(channel_object.id) + ">")


@gompei.command(pass_context=True, aliases=["addAccessRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def add_access_role(ctx, *roles):
    """
    Adds roles to the list that give read access to the server
    Usage: .addAccessRole <role(s)>

    :param ctx: context object
    :param roles: role(s) to add
    """
    if ctx.guild.id != settings["guild_id"]:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to add")
    elif roles[0].lower() == "clear":
        settings["access_roles"] = []
        save_json(os.path.join("config", "settings.json"), settings)
        await ctx.send("Successfully cleared opt-in roles")
    else:
        failed = []
        succeed = []
        already = []
        for role in roles:
            role_object = ctx.guild.get_role(parse_id(role))
            if role_object is None:
                failed.append(role)
            else:
                if role_object.id not in settings["access_roles"]:
                    succeed.append(role_object.name)
                    settings["access_roles"].append(role_object.id)
                else:
                    already.append(role_object.name)

        save_json(os.path.join("config", "settings.json"), settings)

        response = ""
        if len(succeed) > 0:
            response += "\nSuccessfully added access role(s): " + " ".join(succeed)
        if len(already) > 0:
            response += "\nRole(s) " + " ".join(already) + " were already access roles"
        if len(failed) > 0:
            response += "\nFailed to add access role(s): " + " ".join(failed)

        await ctx.send(response)


@gompei.command(pass_context=True, aliases=["removeAccessRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_access_role(ctx, *roles):
    """
    Removes roles from the access list
    Usage: .removeAccessRoles <role(s)>

    :param ctx: context object
    :param roles: role(s) to remove
    """
    if ctx.guild.id != settings["guild_id"]:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to remove")
    elif roles[0].lower() == "clear":
        settings["access_roles"] = []
        save_json(os.path.join("config", "settings.json"), settings)
        await ctx.send("Successfully cleared access roles")
    else:
        failed = []
        succeed = []
        for role in roles:
            if parse_id(role) in settings["access_roles"]:
                settings["access_roles"].remove(parse_id(role))
                role_object = ctx.guild.get_role(parse_id(role))

                if role_object is None:
                    succeed.append(role)
                else:
                    succeed.append(role_object.name)
            else:
                failed.append(role)

        response = ""
        if len(succeed) > 0:
            response += "\nSuccessfully removed access role(s): " + " ".join(succeed)
        if len(failed) > 0:
            response += "\nFailed to remove access role(s): " + " ".join(failed)

        await ctx.send(response)


@gompei.command(pass_context=True, aliases=["addOptInRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def add_opt_in_role(ctx, *roles):
    """
    Adds roles to the opt in list that will be removed if a user loses an access role

    :param ctx: context object
    :param roles: role(s) to add
    """
    if ctx.guild.id != settings["guild_id"]:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to add")
    elif roles[0].lower() == "clear":
        settings["opt_in_roles"] = []
        save_json(os.path.join("config", "settings.json"), settings)
        await ctx.send("Successfully cleared opt-in roles")
    else:
        failed = []
        succeed = []
        already = []
        for role in roles:
            role_object = ctx.guild.get_role(parse_id(role))
            if role_object is None:
                failed.append(role)
            else:
                if role_object.id not in settings["opt_in_roles"]:
                    succeed.append(role_object.name)
                    settings["opt_in_roles"].append(role_object.id)
                else:
                    already.append(role_object.name)

        save_json(os.path.join("config", "settings.json"), settings)

        response = ""
        if len(succeed) > 0:
            response += "\nSuccessfully added opt-in role(s): " + " ".join(succeed)
        if len(already) > 0:
            response += "\nRole(s) " + " ".join(already) + " were already opt-in roles"
        if len(failed) > 0:
            response += "\nFailed to add opt-in role(s): " + " ".join(failed)

        await ctx.send(response)


@gompei.command(pass_context=True, aliases=["removeOptInRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_opt_in_role(ctx, *roles):
    """
    Removes roles from the opt in list
    Usage: .removeOptInRole <role(s)>

    :param ctx: context object
    :param roles: role(s) to remove
    """
    if ctx.guild.id != settings["guild_id"]:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to remove")
    elif roles[0].lower() == "clear":
        settings["opt_in_roles"] = []
        save_json(os.path.join("config", "settings.json"), settings)
        await ctx.send("Successfully cleared opt-in roles")
    else:
        failed = []
        succeed = []
        for role in roles:
            if parse_id(role) in settings["opt_in_roles"]:
                settings["opt_in_roles"].remove(parse_id(role))
                role_object = ctx.guild.get_role(parse_id(role))

                if role_object is None:
                    succeed.append(role)
                else:
                    succeed.append(role_object.name)
            else:
                failed.append(role)

        response = ""
        if len(succeed) > 0:
            response += "\nSuccessfully removed opt-in role(s): " + " ".join(succeed)
        if len(failed) > 0:
            response += "\nFailed to remove opt-in role(s): " + " ".join(failed)

        await ctx.send(response)


@gompei.command(pass_context=True, aliases=["status"])
@commands.check(administrator_perms)
@commands.guild_only()
async def set_status(ctx, *, status):
    """
    Set the bots status ("Now playing <insert>")
    Usage: .status <status>

    :param ctx: context object
    :param status: status
    """
    if len(status) > 128:
        await ctx.send("This status is too long! (128 character limit)")
    else:
        settings["status"] = status
        await gompei.change_presence(activity=discord.Game(name=settings["status"], start=datetime.utcnow()))
        save_json(os.path.join("config", "settings.json"), settings)

        await ctx.send("Successfully updated status")


@gompei.command(pass_context=True)
@commands.check(dm_commands)
async def roll(ctx, number):
    """
    Rolls a die for the number
    Usage: .roll <number>

    :param ctx: context object
    :param number: number of sides on the die
    """
    if "d" in number:
        sides = 0
        try:
            if number[:number.find("d")] != "":
                dice = int(number[:number.find("d")])
            else:
                dice = 1
            sides = int(number[number.find("d") + 1:])
        except ValueError:
            await ctx.send("Could not parse this roll")
            return

        if dice < 1 or sides < 1:
            await ctx.send("Not a valid number of dice/sides")
            return

        total = 0
        response = " ("
        for i in range(0, dice):
            roll_num = random.randint(1, sides)
            total += roll_num
            response += str(roll_num)
            if i == dice - 1:
                break
            response += " + "

        response += " = " + str(total) + ")"

        if dice == 1:
            response = ""

        if ctx.author.nick is not None:
            response = ctx.author.nick.replace("@", "") + " rolled a " + str(total) + "!" + response
        else:
            response = ctx.author.name.replace("@", "") + " rolled a " + str(total) + "!" + response

        if len(response) > 500:
            await ctx.send(response[:response.find("(") - 1])
        else:
            await ctx.send(response)
    else:
        try:
            sides = int(number)
        except ValueError:
            await ctx.send("Could not parse this roll")
            return

        if sides < 1:
            await ctx.send("Not a valid number of sides")
            return

        if ctx.author.nick is not None:
            await ctx.send(ctx.author.nick.replace("@", "") + " rolled a " + str(random.randint(1, sides)) + "!")
        else:
            await ctx.send(ctx.author.name.replace("@", "") + " rolled a " + str(random.randint(1, sides)) + "!")


# Run the bot
gompei.run(sys.argv[1])
