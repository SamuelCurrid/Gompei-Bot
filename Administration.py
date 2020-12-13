from GompeiFunctions import make_ordinal, time_delta_string, load_json, save_json, parse_id
from Permissions import moderator_perms, administrator_perms
from discord.ext import commands
from datetime import timedelta
from datetime import datetime


import pytimeparse
import dateparser
import asyncio
import discord
import Config
import typing
import os


class Administration(commands.Cog):
    """
    Administration tools
    """

    def __init__(self, bot):
        self.warns = load_json(os.path.join("config", "warns.json"))
        self.bot = bot

    async def on_ready(self):
        for member in Config.administration["jails"]:
            seconds = (member["date"] - datetime.now()).total_seconds()

            if seconds < 0:
                seconds = 0

            # Reset roles if some have been picked up since last run
            if member.roles > 1 and seconds > 0:
                if member.premium_since is None:
                    await member.edit(roles=[])
                else:
                    await member.edit(roles=[Config.nitro_role])

            await self.jail_helper(member, seconds, member["roles"])

        muted_role = Config.guild.get_role(615956736616038432)
        for member in Config.administration["mutes"]:
            seconds = (member["date"] - datetime.now()).total_seconds()

            if seconds < 0:
                seconds = 0

            await self.mute_helper(member, seconds, muted_role)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Check role updates to prevent jailed users from accessing the server again

        :param before: Member before
        :param after: Member after
        """
        # Prevent jailed users from picking up roles
        if after in Config.administration["jails"]:
            added_roles = [x for x in after.roles if x not in before.roles]
            if len(added_roles) > 0:
                jail_embed = discord.Embed(title="Member jailed", color=0xbe4041)
                jail_embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)

                jail_embed.description = "<@" + str(after.id) + "> attempted to pick up a role while jailed:\n"
                for role in added_roles:
                    jail_embed.description += "<@&" + str(role.id) + "> "

                jail_embed.set_footer(text="ID: " + str(after.id))
                jail_embed.timestamp = datetime.utcnow()

                await Config.logging["overwrite_channels"]["mod"].send(embed=jail_embed)
                if after.premium_since is None:
                    await after.edit(roles=[])
                else:
                    await after.edit(roles=[Config.nitro_role])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Checks for logging reactions to elevate to staff channel

        :param payload:
        """
        # If a staff channel exists
        if Config.logging["staff"] is not None:
            if Config.guild.id == payload.guild_id:
                channel = Config.guild.get_channel(payload.channel_id)

                # If the channel is a logging channel
                if channel == Config.logging["channel"] or channel == Config.dm_channel or channel in Config.logging["overwrite_channels"].values():
                    if str(payload.emoji) in ["❗", "‼️", "⁉️", "❕"]:
                        message = await channel.fetch_message(payload.message_id)
                        if len(message.embeds) > 0:
                            await Config.logging["staff"].send("Message forwarded by <@" + str(payload.user_id) + "> from <#" + str(channel.id) + ">", embed=message.embeds[0])

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def echo(self, ctx, channel: discord.TextChannel, *, msg: typing.Optional[str]):
        """
        Forwards message / attachments appended to the command to the given channel
        Usage: .echo <channel> <message>

        :param ctx: context object
        :param channel: channel to send the message to
        :param msg: message to send
        """
        # Check for attachments to forward
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        if len(msg) is not None:
            message = await channel.send(msg, files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        elif len(attachments) > 0:
            message = await channel.send(files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        else:
            await ctx.send("No content to send.")

    @commands.command(pass_context=True, aliases=["echoEdit", "editEcho"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def echo_edit(self, ctx, bot_msg: discord.Message, *, msg):
        """
        Edits a message sent by the bot with the message given
        Usage: .echoEdit <messageLink> <message>

        :param ctx: context object
        :param bot_msg: link or id of the message to edit
        :param msg: message to edit to
        """
        # Check if Gompei is author of the message
        if bot_msg.author.id != self.bot.user.id:
            await ctx.send("Cannot edit a message that is not my own")
        else:
            await bot_msg.edit(content=msg)
            await ctx.send("Message edited (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(bot_msg.channel.id) + "/" + str(bot_msg.id) + ">)")

    @commands.command(pass_context=True, aliases=["echoPM", "pmEcho"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def echo_pm(self, ctx, user: typing.Union[discord.User, discord.Member], *, msg):
        """
        Forwards given message / attachments to give user
        Usage: .echoPM <user> <message>

        :param ctx: context object
        :param user: user to send message to
        :param msg: message to send
        """
        # Read attachments and message
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        # Send message to user via DM
        if len(msg) > 0:
            message = await user.send(msg, files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        elif len(attachments) > 0:
            message = await user.send(files=attachments)
            await ctx.send("Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" + str(message.id) + ">)")
        else:
            await ctx.send("No content to send")

        await ctx.message.add_reaction("👍")

    @commands.guild_only()
    @commands.command(pass_context=True, aliases=["pmEdit", "editPM"])
    @commands.check(moderator_perms)
    async def pm_edit(self, ctx, user: typing.Union[discord.Member, discord.User], message_link, *, msg):
        """
        Edits a PM message sent to a user
        Usage: .pmEdit <user> <messageLink>

        :param ctx: context object
        :param user: user that the message was sent to
        :param message_link: link to the message
        :param msg: message to edit to
        """
        # Get message ID from message_link
        message_id = int(message_link[message_link.rfind("/") + 1:])

        channel = user.dm_channel
        if channel is None:
            channel = await user.create_dm()

        message = await channel.fetch_message(message_id)
        if message is None:
            await ctx.send("Not a valid link to message")
        else:
            if message.author.id != self.bot.user.id:
                await ctx.send("Cannot edit a message that is not my own")
            else:
                await message.edit(content=msg)
                await ctx.send("Message edited (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(channel.id) + "/" + str(message_id) + ">)")

    @commands.command(pass_context=True, aliases=["echoReact", "react"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def echo_react(self, ctx, message: discord.Message, emote: typing.Union[discord.Emoji, str]):
        """
        Adds a reaction to a message
        Usage: .echoReact <message> <emote>

        :param ctx: context object
        :param message: message link or ID
        :param emote: emote to react with
        """
        await message.add_reaction(emote)
        await ctx.message.add_reaction("👍")

    @commands.command(pass_context=True, aliases=["echoRemoveReact", "reactRemove"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def echo_remove_react(self, ctx, message: discord.Message, emote: typing.Union[discord.Emoji, str]):
        """
        Removes the bots reaction from a message
        Usage: .echoRemoveReact <message> <emote>

        :param ctx: context object
        :param message: message link or ID
        :param emote: emote to un-react with
        """
        await message.remove_reaction(emote)
        await ctx.message.add_reaction("👍")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def purge(self, ctx, channel: typing.Optional[discord.TextChannel], *, number: int = 0):
        """
        Deletes given number of messages in a channel
        Usage: .purge (channel) <number>

        :param ctx: context object
        :param channel: (optional) channel to purge from
        :param number: number of messages to purge
        """
        if channel is None:
            await ctx.channel.purge(limit=int(number) + 1)
        else:
            await channel.purge(limit=int(number))

    @commands.command(pass_context=True, aliases=["selectivePurge", "spurge"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def selective_purge(self, ctx, target: typing.Union[discord.User, discord.TextChannel], user: typing.Optional[discord.User], *, number: int = 0):
        """
        Purges messages from a specific user in a channel
        Usage: .spurge (channel) <user> <number>

        :param ctx: context object
        :param target: member or channel to purge from
        :param user: user to purge if a channel is given
        :param number: number of messages to purge
        """
        messages = []
        count = 0

        if isinstance(target, discord.User):
            channel = ctx.message.channel
            messages.append(ctx.message)
            user = target
        else:
            channel = target

        old_message = (await channel.history(limit=1).flatten())[0].created_at

        while count < int(number):
            async for message in channel.history(limit=int(number), before=old_message, oldest_first=False):
                if message.author.id == user.id:
                    count += 1
                    messages.append(message)

                    if count == int(number):
                        break

                old_message = message.created_at

        await channel.delete_messages(messages)

    @commands.command(pass_context=True, aliases=["tPurge", "timePurge"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def time_purge(self, ctx, channel: typing.Optional[discord.TextChannel], *, time1, time2=None):
        """
        Purges messages from a time range in a channel
        Usage: .timePurge (channel) <startTime> (endTime)

        :param ctx: context object
        :param channel: (optional) channel to purge from
        :param time1: time to start purge at
        :param time2: (optional) time to end purge at
        """
        if channel is None:
            channel = ctx.message.channel

        after_date = dateparser.parse(time1)

        if after_date is None:
            await ctx.send("Not a valid after time/date")
            return

        if time2 is None:
            offset = datetime.utcnow() - datetime.now()
            messages = await channel.history(limit=None, after=after_date + offset).flatten()
        else:
            before_date = dateparser.parse(time2)

            if before_date is None:
                await ctx.send("Not a valid before time/date")
                return

            offset = datetime.utcnow() - datetime.now()
            messages = await channel.history(limit=None, after=after_date + offset, before=before_date + offset).flatten()

        if len(messages) == 0:
            await ctx.send("There are no messages to purge in this time frame")
            return

        response = "You are about to purge " + str(len(messages)) + " message(s) from " + channel.name
        if time2 is None:
            response += " after " + str(after_date) + ".\n"
        else:
            response += " between " + str(after_date) + " and " + str(before_date) + ".\n"

        response += "The purge will start at <" + messages[0].jump_url + "> and end at <" + messages[-1].jump_url + ">.\n\nAre you sure you want to proceed? (Y/N)"

        def check_author(message):
            return message.author.id == ctx.author.id

        query = await ctx.send(response)

        response = await self.bot.wait_for('message', check=check_author)
        if response.content.lower() == "y" or response.content.lower() == "yes":
            if channel.id == ctx.channel.id:
                messages.append(response)
                messages.append(query)
                await channel.delete_messages(messages)
            else:
                await channel.delete_messages(messages)
                await ctx.send("Successfully purged messages")
        else:
            await ctx.send("Cancelled purging messages")

    @commands.command(pass_context=True, aliases=["mPurge", "messagePurge"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def message_purge(self, ctx, start_message: discord.TextChannel, end_message: discord.TextChannel = None):
        """
        Purges messages from an inclusive range of messages
        Usage: .messagePurge <startMessage> (endMessage)

        :param ctx: context object
        :param start_message: first message to purge
        :param end_message: (optional) last message to purge
        """
        if end_message is None:
            messages = await start_message.channel.history(limit=None, after=start_message.created_at).flatten()
        else:
            if start_message.channel.id != end_message.channel.id:
                await ctx.send("End message is not in the same channel as the start message")
                return

            messages = await start_message.channel.history(limit=None, after=start_message.created_at, before=end_message.created_at).flatten()
            messages.append(end_message)

        messages.insert(0, start_message)

        if len(messages) == 0:
            await ctx.send("You've selected no messages to purge")
            return

        response = "You are about to purge " + str(len(messages)) + " message(s) from " + start_message.channel.name

        response += "\nThe purge will start at <" + messages[0].jump_url + "> and end at <" + messages[-1].jump_url + ">.\n\nAre you sure you want to proceed? (Y/N)"

        def check_author(message):
            return message.author.id == ctx.author.id

        query = await ctx.send(response)

        response = await self.bot.wait_for('message', check=check_author)

        if response.content.lower() == "y" or response.content.lower() == "yes":
            if start_message.channel.id == ctx.channel.id:
                messages.append(response)
                messages.append(query)
                await start_message.channel.delete_messages(messages)
            else:
                await start_message.channel.delete_messages(messages)
                await ctx.send("Successfully purged messages")
        else:
            await ctx.send("Cancelled purging messages")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, time, *, reason):
        """
        Mutes a member for the given time and reason
        Usage: .mute <member> <time> <reason>

        :param ctx: context object
        :param member: member to mute
        :param time: time to mute for
        :param reason: reason for the mute (dm'ed to the user)
        """
        muted_role = ctx.guild.get_role(615956736616038432)

        # Is user already muted
        if muted_role in member.roles:
            await ctx.send("This member is already muted")
            return

        # Check role hierarchy
        if ctx.author.top_role.position <= member.top_role.position:
            await ctx.send("You're not high enough in the role hierarchy to do that.")
            return

        username = member.name + "#" + str(member.discriminator)

        seconds = pytimeparse.parse(time)
        if seconds is None:
            await ctx.send("Not a valid time, try again")

        delta = timedelta(seconds=seconds)
        if len(reason) < 1:
            await ctx.send("You must include a reason for the mute")
            return

        Config.add_mute(member, datetime.now() + timedelta(seconds=seconds))

        mute_time = time_delta_string(datetime.utcnow(), datetime.utcnow() + delta)

        mute_embed = discord.Embed(title="Member muted", color=0xbe4041)
        mute_embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
        mute_embed.description = "**Muted:** <@" + str(member.id) + ">\n**Time:** " + mute_time + "\n**__Reason__**\n> " + reason + "\n\n**Muter:** <@" + str(ctx.author.id) + ">"
        mute_embed.set_footer(text="ID: " + str(member.id))
        mute_embed.timestamp = datetime.utcnow()

        await member.add_roles(muted_role)
        await ctx.send("**Muted** user **" + username + "** for **" + mute_time + "** for: **" + reason + "**")
        await Config.logging["overwrite_channels"]["mod"].send(embed=mute_embed)
        await member.send("**You were muted in the WPI Discord Server for " + mute_time + ". Reason:**\n> " + reason + "\n\nYou can respond here to contact WPI Discord staff.")

        await self.mute_helper(member, seconds, muted_role)

    async def mute_helper(self, member, seconds, muted_role):
        """
        Waits out the jail time before returning roles to a user

        :param member: Member who is jailed
        :param seconds: Seconds to wait
        :param muted_role: Role to remove for unmute
        """
        await asyncio.sleep(seconds)
        Config.remove_mute(member)
        await member.remove_roles(muted_role)

        mute_embed = discord.Embed(title="Member unmuted", color=0x43b581)
        mute_embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
        mute_embed.description = "Unmuted <@" + str(member.id) + ">"
        mute_embed.set_footer(text="ID: " + str(member.id))
        mute_embed.timestamp = datetime.utcnow()

        await Config.logging["overwrite_channels"]["mod"].send(embed=mute_embed)

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Warns a specific user for given reason
        Usage: .warn <member> <reason>

        :param ctx: context object
        :param member: member of the server to warn
        :param reason: reason to log and DM
        """
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        if len(reason) > 0:
            await member.send("You were warned in the WPI Discord Server. Reason:\n> " + reason, files=attachments)
        else:
            await ctx.send("No warning to send")
            return

        if str(member.id) in self.warns:
            self.warns[str(member.id)].append(reason)
        else:
            self.warns[str(member.id)] = [reason]

        save_json(os.path.join("config", "warns.json"), self.warns)

        await ctx.send("Warning sent to " + member.display_name + " (" + str(member.id) + "), this is their " + make_ordinal(len(self.warns[str(member.id)])) + " warning")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def warns(self, ctx, user: typing.Union[discord.Member, discord.User] = None):
        """
        List the warns for the server or a user
        Usage: .warns (user)

        :param ctx: context object
        :param user: (optional) user in the server
        """
        message = ""
        if user is None:
            if len(self.warns) == 0:
                message = "There are no warnings on this server"
            for user in self.warns:
                message += "Warnings for <@" + user + ">\n"
                count = 1
                for warn in self.warns[user]:
                    message += "__**" + str(count) + ".**__\n" + warn + "\n\n"
                    count += 1

                message += "\n\n"
        else:
            if str(user.id) in self.warns:
                message = "Warnings for <@" + str(user.id) + ">\n"
                for warn in self.warns[str(user.id)]:
                    message += "> " + warn + "\n"
            else:
                message = "This user does not exist or has no warnings"

        if len(message) > 2000:
            n = 2000
            for index in range(0, len(message), n):
                await ctx.send(message[index: index + n])
        else:
            await ctx.send(message)

    @commands.command(pass_context=True, aliases=["warnNote"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def warn_note(self, ctx, user: typing.Union[discord.Member, discord.User], *, reason):
        """
        Adds a warning to a user without DM'ing them
        Usage: .warnNote <user> <reason>

        :param ctx: context object
        :param user: user to add a note for
        :param reason: reason for the note
        """
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        if str(user.id) in self.warns:
            self.warns[str(user.id)].append(reason)
        else:
            self.warns[str(user.id)] = [reason]

        save_json(os.path.join("config", "warns.json"), self.warns)

        if isinstance(user, discord.Member):
            await ctx.send("Warning added for " + user.display_name + " (" + str(user.id) + "), this is their " + make_ordinal(len(self.warns[str(user.id)])) + " warning")
        else:
            await ctx.send("Warning added for " + user.name + " (" + str(user.id) + "), this is their " + make_ordinal(len(self.warns[str(user.id)])) + " warning")

    @commands.command(pass_context=True, aliases=["clearWarn"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def clear_warn(self, ctx, user: typing.Union[discord.Member, discord.User]):
        """
        Clears the warnings for a user
        Usage: .clearWarn <user>

        :param ctx: context object
        :param user: user to clear warns for
        """
        if str(user.id) in self.warns:
            del self.warns[str(user.id)]
            await ctx.send("Cleared warnings for <@" + str(user.id) + ">")
            save_json(os.path.join("config", "warns.json"), self.warns)
        else:
            await ctx.send("This user does not exist or has no warnings")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        """
        Locks down a channel so users cannot send messages in it
        Usage: .lockdown (channel)

        :param ctx: context object
        :param channel: (optional) channel to lockdown
        """
        if channel is None:
            lock_channel = ctx.channel
        else:
            lock_channel = channel

        overwrite = lock_channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            await ctx.send("Channel is already locked down!")
        else:
            overwrite.update(send_messages=False)
            await lock_channel.send(":lock: **This channel is now locked**")
            await lock_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """
        Unlocks a channel that is locked
        Usage: .unlock (channel)

        :param ctx: context object
        :param channel: (optional) channel to unlock
        """
        if channel is None:
            lock_channel = ctx.channel
        else:
            lock_channel = channel

        overwrite = lock_channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            overwrite.update(send_messages=None)
            await lock_channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await lock_channel.send(":unlock: **Unlocked the channel**")
        else:
            await ctx.send("Channel is not locked")

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def jail(self, ctx, member: discord.Member, time: str, *, reason: str):
        """
        Jails a member from the server by removing all of their roles
        Usage: .jail <member> <time> <reason>

        :param ctx: Context object
        :param member: Member to jail
        :param time: Time to jail for
        :param reason: Reason for the jail
        """
        # Is user already jailed
        if member in Config.administration["jails"]:
            await ctx.send("This member is already jailed")
            return

        # Check role hierarchy
        if ctx.author.top_role.position <= member.top_role.position:
            await ctx.send("You're not high enough in the role hierarchy to do that.")
            return

        roles = member.roles

        seconds = pytimeparse.parse(time)
        if seconds is None:
            await ctx.send("Not a valid time, try again")

        delta = timedelta(seconds=seconds)
        jail_time = time_delta_string(datetime.utcnow(), datetime.utcnow() + delta)

        if len(reason) < 1:
            await ctx.send("You must include a reason for the jail")
            return

        Config.add_jail(member, datetime.now() + timedelta(seconds=seconds), roles)

        jail_embed = discord.Embed(title="Member jailed", color=0xbe4041)
        jail_embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
        jail_embed.description = "**Muted:** <@" + str(member.id) + ">\n**Time:** " + jail_time + "\n**__Reason__**\n> " + reason + "\n\n**Muter:** <@" + str(ctx.author.id) + ">"
        jail_embed.set_footer(text="ID: " + str(member.id))
        jail_embed.timestamp = datetime.utcnow()

        if member.premium_since is None:
            await member.edit(roles=[])
        else:
            await member.edit(roles=[Config.nitro_role])

        await member.send("You have been locked out of the server for " + jail_time + ". Reason:\n> " + reason + "\n\nYou can respond here to contact WPI Discord staff.")
        await Config.logging["overwrite_channels"]["mod"].send(embed=jail_embed)
        await ctx.send("**Jailed** user **" + member.display_name + "** for **" + jail_time + "** for: **" + reason + "**")
        await self.jail_helper(member, seconds, roles)

    async def jail_helper(self, member, seconds, roles):
        """
        Waits out the jail time before returning roles to a user

        :param member: Member who is jailed
        :param seconds: Seconds to wait
        :param roles: Roles to return
        """
        await asyncio.sleep(seconds)
        Config.remove_jail(member)
        await member.edit(roles=roles)

        jail_embed = discord.Embed(title="Member unjailed", color=0x43b581)
        jail_embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
        jail_embed.description = "Unjailed <@" + str(member.id) + ">"
        jail_embed.set_footer(text="ID: " + str(member.id))
        jail_embed.timestamp = datetime.utcnow()

        await Config.logging["overwrite_channels"]["mod"].send(embed=jail_embed)

    @commands.command(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def slowmode(self, ctx, channel: typing.Optional[discord.TextChannel], *, time):
        """
        Sets the slowmode in a channel
        Usage: .slowmode (channel) <time>

        :param ctx: context object
        :param channel: (optional) channel to set slowmode on
        :param time: time for the slowmode
        """
        if channel is None:
            channel = ctx.message.channel

        seconds = pytimeparse.parse(time)
        if seconds is None:
            await ctx.send("Not a valid time format, try again")
        elif seconds > 21600:
            await ctx.send("Slowmode delay is too long")
        else:
            await channel.edit(slowmode_delay=seconds)
            await ctx.send("Successfully set slowmode delay to " + str(seconds) + " seconds in #" + channel.name)

    @commands.command(pass_context=True)
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason):
        """
        Kicks a user from the server with a DM'ed reason
        Usage: .kick <member> <reason>

        :param ctx: context object
        :param member: member to kick
        :param reason: reason to kick, DM'ed to user
        """
        if len(reason) < 1:
            await ctx.send("Must include a reason with the kick")
        else:
            await member.send(member.guild.name + " kicked you for reason:\n> " + reason)
            await member.kick(reason=reason)
            await ctx.send("Successfully kicked user " + member.name + member.discriminator)

    @commands.command(pass_context=True)
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason):
        """
        Bans a user from the server, requires a reason as well
        Usage: .ban <member> <reason>

        :param ctx: context object
        :param member: member to ban
        :param reason: reason for the ban, DM'ed to user
        """
        if len(reason) < 1:
            await ctx.send("Must include a reason with the ban")
        else:
            await member.send(member.guild.name + " banned you for reason:\n> " + reason)
            await member.kick(reason=reason)
            await ctx.send("Successfully banned user " + member.name + member.discriminator)

    @commands.command(pass_context=True, name="modLog")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def change_mod_log(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel in which to log mod actions into
        Usage: .modLog <channel>

        :param ctx: context object
        :param channel: channel
        """
        if Config.raw_settings["mod_log"] != channel.id:
            Config.set_mod_log(channel)
            await ctx.send("Successfully updated mod log channel")
        else:
            await ctx.send("This is already the mod log channel")

    @commands.command(pass_context=True, name="staffChannel")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def change_staff_channel(self, ctx, channel: discord.TextChannel):
        if Config.logging["staff"] != channel:
            Config.set_staff_channel(channel)
            await ctx.send("Successfully updated staff channel")
        else:
            await ctx.send("This is already the staff channel")
