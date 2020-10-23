from GompeiFunctions import make_ordinal, timeDeltaString, load_json, save_json, parse_id
from Permissions import moderator_perms
from discord.ext import commands
from datetime import timedelta
from datetime import datetime
from pytimeparse import parse

import asyncio
import os


class Administration(commands.Cog):
    """
    Administration tools
    """

    def __init__(self, bot):
        self.warns = load_json(os.path.join("config", "warns.json"))
        self.bot = bot

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def echo(self, ctx, channel):
        """
        Forwards message / attachments appended to the command to the given channel
        :param ctx: context object
        :param channel: channel to send the message to
        """
        channel = ctx.guild.get_channel(int(channel[2:-1]))

        # Check if the channel exists
        if channel is not None:

            # Check for attachments to forward
            attachments = []
            if len(ctx.message.attachments) > 0:
                for i in ctx.message.attachments:
                    attachments.append(await i.to_file())

            # Get message content and check length
            message = ctx.message.content[7 + len(channel):]
            if len(message) > 0:
                message = await channel.send(message, files=attachments)
                await ctx.send("Message sent (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id) + ">)")
            elif len(attachments) > 0:
                message = await channel.send(files=attachments)
                await ctx.send("Message sent (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id) + ">)")
            else:
                await ctx.send("No content to send.")
        else:
            await ctx.send("Not a valid channel")

    @echo.error
    async def echo_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for echo command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments")
        else:
            print(error)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def echoEdit(self, ctx, messageLink):
        messageID = int(messageLink[messageLink.rfind("/") + 1:])
        shortLink = messageLink[:messageLink.rfind("/")]
        channelID = int(shortLink[shortLink.rfind("/") + 1:])

        channel = ctx.guild.get_channel(channelID)
        if channel is None:
            await ctx.send("Not a valid link to message")
        else:
            message = await channel.fetch_message(messageID)
            if message is None:
                await ctx.send("Not a valid link to message")
            else:
                if message.author.id != self.bot.user.id:
                    await ctx.send("Cannot edit a message that is not my own")
                else:
                    newMessage = ctx.message.content[10 + len(messageLink):]

                    await message.edit(content=newMessage)
                    await ctx.send("Message edited (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(channelID) + "/" + str(messageID) + ">)")

    @commands.guild_only()
    @commands.command(pass_context=True, aliases=['pmEcho'])
    @commands.check(moderator_perms)
    async def echoPM(self, ctx, arg1):
        """
        Fowards given message / attachments to give user
        """
        member = ctx.guild.get_member(parse_id(arg1))

        if member is None:
            await ctx.send("Not a valid member")
            return

        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        message = ctx.message.content[9 + len(arg1):]
        if len(message) > 0:
            message = await member.send(message, files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        elif len(attachments) > 0:
            message = await member.send(files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        else:
            await ctx.send("No content to send")

        await ctx.message.add_reaction("👍")

    @echoPM.error
    async def echoPM_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for echo command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments")
        else:
            print(error)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def pmEdit(self, ctx, user, messageLink):
        messageID = int(messageLink[messageLink.rfind("/") + 1:])

        member = ctx.guild.get_member(parse_id(user))
        if member is None:
            await ctx.send("Not a valid user")
        else:
            channel = member.dm_channel
            if channel is None:
                channel = await member.create_dm()

            message = await channel.fetch_message(messageID)
            if message is None:
                await ctx.send("Not a valid link to message")
            else:
                if message.author.id != self.bot.user.id:
                    await ctx.send("Cannot edit a message that is not my own")
                else:
                    newMessage = ctx.message.content[10 + len(messageLink) + len(user):]

                    await message.edit(content=newMessage)
                    await ctx.send("Message edited (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(channel.id) + "/" + str(messageID) + ">)")

    @commands.guild_only()
    @commands.command(pass_context=True, aliases=['react'])
    @commands.check(moderator_perms)
    async def echoReact(self, ctx, message_link, emote):
        messageID = int(message_link[message_link.rfind("/") + 1:])
        shortLink = message_link[:message_link.rfind("/")]
        channelID = int(shortLink[shortLink.rfind("/") + 1:])

        channel = ctx.guild.get_channel(channelID)
        if channel is None:
            await ctx.send("Not a valid link to message")
        else:
            message = await channel.fetch_message(messageID)
            if message is None:
                await ctx.send("Not a valid link to message")
            else:
                await message.add_reaction(emote)
                await ctx.message.add_reaction("👍")

    @commands.guild_only()
    @commands.command(pass_context=True, aliases=['reactRemove'])
    @commands.check(moderator_perms)
    async def echoRemoveReact(self, ctx, message_link, emote):
        messageID = int(message_link[message_link.rfind("/") + 1:])
        shortLink = message_link[:message_link.rfind("/")]
        channelID = int(shortLink[shortLink.rfind("/") + 1:])

        channel = ctx.guild.get_channel(channelID)
        if channel is None:
            await ctx.send("Not a valid link to message")
        else:
            message = await channel.fetch_message(messageID)
            if message is None:
                await ctx.send("Not a valid link to message")
            else:
                await message.remove_reaction(emote)
                await ctx.message.add_reaction("👍")

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def purge(self, ctx, arg1):
        """
        Purges a number of messages in channel used
        :param ctx: context object
        :param arg1: number of messages to purge
        """
        await ctx.channel.purge(limit=int(arg1) + 1)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for purge command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments")
        else:
            print(error)

    @commands.guild_only()
    @commands.command(pass_context=True, name="spurge")
    @commands.check(moderator_perms)
    async def selective_purge(self, ctx, arg1, arg2):
        """
        Purges messages from a specific user in the channel
        :param ctx: context object
        :param arg1: user to purge
        :param arg2: number of messages to purge
        """
        member = ctx.guild.get_member(parse_id(arg1))

        messages = [ctx.message]
        oldMessage = ctx.message
        count = 0

        while count < int(arg2):
            async for message in ctx.message.channel.history(limit=int(arg2), before=oldMessage, oldest_first=False):
                if message.author == member:
                    count += 1
                    messages.append(message)

                    if count == int(arg2):
                        break

                oldMessage = message.created_at

        await ctx.channel.delete_messages(messages)

    @selective_purge.error
    async def selective_purge_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for selective purge command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments")
        else:
            print(error)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def mute(self, ctx, arg1, arg2):
        member = ctx.guild.get_member(parse_id(arg1))
        mutedRole = ctx.guild.get_role(615956736616038432)

        # Is user already muted
        if mutedRole in member.roles:
            await ctx.send("This member is already muted")
            return

        # Check role hierarchy
        if ctx.author.top_role.position <= member.top_role.position:
            await ctx.send("You're not high enough in the role hierarchy to do that.")
            return

        username = member.name + "#" + str(member.discriminator)

        seconds = parse(arg2)
        if seconds is None:
            await ctx.send("Not a valid time, try again")

        delta = timedelta(seconds=seconds)
        reason = ctx.message.content[8 + len(arg1 + arg2):]
        if len(reason) < 1:
            await ctx.send("You must include a reason for the mute")
            return

        muteTime = timeDeltaString(datetime.utcnow(), datetime.utcnow() + delta)

        await member.add_roles(mutedRole)
        await ctx.send("**Muted** user **" + username + "** for **" + muteTime + "** for: **" + reason + "**")
        await member.send("**You were muted in the WPI Discord Server for " + muteTime + ". Reason:**\n> " + reason + "\n\nYou can repond here to contact WPI Discord staff.")

        await asyncio.sleep(seconds)

        await member.remove_roles(mutedRole)
        await ctx.send("**Unmuted** user **" + username + "**")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments: .mute <user> <minutes> <reason>")
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid mute time")

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def warn(self, ctx, user):
        """
        Warns a specific user for given reason
        """
        memberID = parse_id(user)
        member = ctx.guild.get_member(memberID)

        if member is None:
            await ctx.send("Not a valid member")
            return

        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        message = ctx.message.content[7 + len(user):]
        if len(message) > 0:
            await member.send("You were warned in the WPI Discord Server. Reason:\n> " + message, files=attachments)
        else:
            await ctx.send("No warning to send")
            return

        if str(memberID) in self.warns:
            self.warns[str(memberID)].append(message)
        else:
            self.warns[str(memberID)] = [message]

        save_json(os.path.join("config", "warns.json"), self.warns)

        await ctx.send("Warning sent to " + member.display_name + " (" + str(memberID) + "), this is their " + make_ordinal(len(self.warns[str(memberID)])) + " warning")

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for warn command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments\n> warn [user/user_ID] [reason]")
        else:
            print(error)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def warns(self, ctx, user=None):
        message = ""
        if user is None:
            if len(self.warns) == 0:
                message = "There are no warnings on this server"
            for member in self.warns:
                message += "Warnings for <@" + member + ">\n"
                count = 1
                for warn in self.warns[member]:
                    message += "__**" + str(count) + ".**__\n" + warn + "\n\n"
                    count += 1

                message += "\n\n"
        else:
            memberID = parse_id(user)
            if str(memberID) in self.warns:
                message = "Warnings for <@" + str(memberID) + ">\n"
                for warn in self.warns[str(memberID)]:
                    message += "> " + warn + "\n"
            else:
                message = "This user does not exist or has no warnings"

        if len(message) > 2000:
            n = 2000
            for index in range(0, len(message), n):
                await ctx.send(message[index: index + n])
        else:
            await ctx.send(message)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def warnNote(self, ctx, user):
        memberID = parse_id(user)
        member = ctx.guild.get_member(memberID)

        if member is None:
            await ctx.send("Not a valid member")
            return

        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        message = ctx.message.content[11 + len(user):]

        if str(memberID) in self.warns:
            self.warns[str(memberID)].append(message)
        else:
            self.warns[str(memberID)] = [message]

        save_json(os.path.join("config", "warns.json"), self.warns)

        await ctx.send("Warning added for " + member.display_name + " (" + str(memberID) + "), this is their " + make_ordinal(len(self.warns[str(memberID)])) + " warning")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def clearWarn(self, ctx, user):
        memberID = parse_id(user)
        if str(memberID) in self.warns:
            del self.warns[str(memberID)]
            await ctx.send("Cleared warnings for <@" + str(memberID) + ">")
            save_json(os.path.join("config", "warns.json"), self.warns)
        else:
            await ctx.send("This user does not exist or has no warnings")

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def lockdown(self, ctx):
        if len(ctx.message.content) > 10:
            lockChannel = ctx.guild.get_channel(parse_id(ctx.message.content[10:]))
            if lockChannel is None:
                await ctx.send("Not a valid channel to lockdown")
                return
        else:
            lockChannel = ctx.channel

        overwrite = lockChannel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            await ctx.send("Channel is already locked down!")
        else:
            overwrite.update(send_messages=False)
            await lockChannel.send(":white_check_mark: **Locked down " + lockChannel.name + "**")
            await lockChannel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    async def unlock(self, ctx):
        if len(ctx.message.content) > 8:
            lockChannel = ctx.guild.get_channel(parse_id(ctx.message.content[8:]))
            if lockChannel is None:
                await ctx.send("Not a valid channel to unlock")
                return
        else:
            lockChannel = ctx.channel

        overwrite = lockChannel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            overwrite.update(send_messages=None)
            await lockChannel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await lockChannel.send(":white_check_mark: **Unlocked " + lockChannel.name + "**")
        else:
            await ctx.send("Channel is not locked")
