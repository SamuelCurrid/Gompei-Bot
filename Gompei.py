from GompeiFunctions import load_json, save_json, parse_id, time_delta_string
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
import Config
import random
import json
import os
import sys

greetings = ["hello", "hi", "greetings", "howdy", "salutations", "hey", "oi", "dear", "yo ", "morning", "afternoon", "evening", "sup", "G'day", "good day", "bonjour"]
gompei_references = ["gompei", "672453835863883787", "goat"]
love_references = ["gompeiHug", "love", "ily", "<3", "❤"]
hate_references = ["fuck you", "sucks", "fucker", "idiot", "shithead", "eat shit", "hate"]
violent_references = ["kill", "murder", "attack", "skin", "ambush", "stab"]


def get_prefix(client, message):
    return Config.prefix


# Initialize Bot
intents = discord.Intents.default()
intents.members = True
intents.presences = True
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
async def on_message(message):
    """
    Forwards DM messages to the DM channel

    :param message: message
    """
    if not message.author.bot:
        await gompei.process_commands(message)

        if message.author.id == 87585011070414848 and "beep beep" in message.content.lower():
            await message.channel.send("https://i.pinimg.com/originals/84/ee/27/84ee27382f9f9819097b29fe78be814d.png")

        if isinstance(message.channel, discord.channel.DMChannel) and Config.dm_channel is not None:

            message_embed = discord.Embed(description=message.content, timestamp=datetime.utcnow())
            message_embed.set_author(name="DM from " + message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
            message_embed.set_footer(text=message.author.id)

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
                await Config.dm_channel.send(embed=message_embed)
                await Config.dm_channel.send(files=attachments)
            else:
                await Config.dm_channel.send(embed=message_embed)
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
    Forwards DM messages edited in DMs to a channel

    :param before: message before edit
    :param after: message after edit
    """
    if isinstance(before.channel, discord.channel.DMChannel) and not before.author.bot and Config.dm_channel is not None:
        if before.content is after.content:
            return

        message_embed = discord.Embed(timestamp=datetime.utcnow())
        message_embed.colour = discord.Colour(0x8899d4)
        message_embed.set_author(name=after.author.name + "#" + before.author.discriminator, icon_url=after.author.avatar_url)
        message_embed.title = "Message edited by " + after.author.name + "#" + str(after.author.discriminator)
        message_embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
        message_embed.set_footer(text="ID: " + str(before.author.id))
        message_embed.timestamp = datetime.utcnow()

        await Config.dm_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_edit(payload):
    """
    Forwards DM uncached message edits to the DM channel

    :param payload: uncached message edit payload
    """
    # If the message is not cached
    if payload.cached_message is None:
        guild = Config.guild
        dm_channel = Config.dm_channel
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
    """
    Forwards DM message delete events to the DM channel

    :param message: Message that was deleted
    """
    # If a DM message
    if isinstance(message.channel, discord.channel.DMChannel) and not message.author.bot and Config.dm_channel is not None:
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

        await Config.dm_channel.send(embed=message_embed)


@gompei.event
async def on_raw_message_delete(payload):
    """
    Forwards DM uncached message delete events to the DM channel

    :param payload: Uncached deleted message payload
    """
    # If a DM message
    if not hasattr(payload, "guild_id") and Config.dm_channel is not None:
        # If the message is not cached
        if payload.cached_message is None:
            message_embed = discord.Embed()
            message_embed.colour = discord.Colour(0xbe4041)
            message_embed.title = "Message deleted by ???"
            message_embed.set_footer(text="Uncached message: " + str(payload.message_id))
            message_embed.timestamp = datetime.utcnow()

            await Config.dm_channel.send(embed=message_embed)


@gompei.event
async def on_typing(channel, user, when):
    """
    Sends an on typing event to DM channel if someone is typing in the bots DMs

    :param channel: channel that the user is typing in
    :param user: user that is typing
    :param when: when the user was typing
    """
    if isinstance(channel, discord.channel.DMChannel) and not user.bot and Config.dm_channel is not None:
        await Config.dm_channel.trigger_typing()


@gompei.event
async def on_member_update(before, after):
    """
    Removes opt in channel roles if losing access role

    :param before: member roles before
    :param after: member roles after
    """
    # Role checks
    added_roles = [x for x in after.roles if x not in before.roles]
    removed_roles = [x for x in before.roles if x not in after.roles]

    for role in added_roles:
        if role.id == 630589807084699653:
            await after.send("Welcome to the WPI Discord Server!\n\nIf you have any prospective student questions, feel free to shoot them in #help-me. Hopefully we, or someone else in the community, can answer them :smile:.")

    # If roles edited
    if len(added_roles) + len(removed_roles) > 0:
        role_list = []
        for role in after.roles:
            if role in Config.access_roles:
                return
            if role not in Config.opt_in_roles:
                role_list.append(role)

        await after.edit(roles=role_list)


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
        help_embed = discord.Embed(title="Gompei Bot", colour=discord.Colour.blue())
        help_embed.add_field(name="Documentation", value="https://samuelcurrid.github.io/Gompei-Bot/documentation.html")
        help_embed.set_thumbnail(url="https://raw.githubusercontent.com/SamuelCurrid/Gompei-Bot/master/assets/gompei.png")
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


@gompei.command(pass_context=True)
@commands.check(dm_commands)
async def lockout(ctx):
    """
    Removes user roles and stores them to be returned after
    Usage: .lockout

    :param ctx: context object
    """
    member = await Config.guild.fetch_member(ctx.message.author.id)

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
            await member.edit(roles=[Config.nitro_role])

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
    guild = Config.guild
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
    if ctx.guild != Config.guild:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    else:
        if channel.lower() == "clear":
            Config.clear_dm_channel()
            await ctx.send("Disabled the DM channel")
        else:
            channel_object = ctx.guild.get_channel(parse_id(channel))

            if channel_object is None:
                await ctx.send("Not a valid channel")
            elif channel_object == Config.dm_channel:
                await ctx.send("This is already the DM channel")
            else:
                Config.set_dm_channel(channel_object)
                await ctx.send("Successfully updated DM channel to <#" + str(channel_object.id) + ">")


@gompei.command(pass_context=True, aliases=["addAccessRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def add_access_role(ctx, *roles: discord.Role):
    """
    Adds roles to the list that give read access to the server
    Usage: .addAccessRole <role(s)>

    :param ctx: context object
    :param roles: role(s) to add
    """
    if ctx.guild != Config.guild:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to add")
    else:
        Config.add_access_roles(roles)
        await ctx.send("Successfully added roles")


@gompei.command(pass_context=True, aliases=["removeAccessRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_access_role(ctx, *roles: discord.Role):
    """
    Removes roles from the access list
    Usage: .removeAccessRoles <role(s)>

    :param ctx: context object
    :param roles: role(s) to remove
    """
    if ctx.guild != Config.guild:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to remove")
    else:
        Config.remove_access_roles(roles)
        await ctx.send("Successfully removed roles")


@gompei.command(pass_context=True, aliases=["addOptInRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def add_opt_in_role(ctx, *roles: discord.Role):
    """
    Adds roles to the opt in list that will be removed if a user loses an access role

    :param ctx: context object
    :param roles: role(s) to add
    """
    if ctx.guild != Config.guild:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to add")
    else:
        Config.add_opt_in_roles(roles)
        await ctx.send("Successfully added roles")


@gompei.command(pass_context=True, aliases=["removeOptInRole"])
@commands.check(administrator_perms)
@commands.guild_only()
async def remove_opt_in_role(ctx, *roles: discord.Role):
    """
    Removes roles from the opt in list
    Usage: .removeOptInRole <role(s)>

    :param ctx: context object
    :param roles: role(s) to remove
    """
    if ctx.guild != Config.guild:
        await ctx.send("This bot isn't configured to work in this server! Read instructions on how to set it up here: <INSERT LINK>")
    elif len(roles) == 0:
        await ctx.send("You must include a role to remove")
    else:
        Config.remove_opt_in_roles(roles)
        await ctx.send("Successfully removed roles")


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
