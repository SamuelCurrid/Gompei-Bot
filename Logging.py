from GompeiFunctions import make_ordinal, time_delta_string
from Permissions import administrator_perms
from discord.ext import commands
from datetime import datetime

import discord
import Config


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = discord.Embed()
        self.statuses = {}

    @commands.command(pass_context=True, name="logging")
    @commands.check(administrator_perms)
    async def change_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends logging messages in
        Usage: .logging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["channel"] != channel:
            Config.set_logging_channel(channel)
            await ctx.send("Successfully updated logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for logging")

    @commands.command(pass_context=True, name="memberLogging")
    @commands.check(administrator_perms)
    async def change_member_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends member logging messages in
        Usage: .memberLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["member"] != channel:
            Config.set_overwrite_logging_channel("member", channel)
            await ctx.send("Successfully updated member logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for member logging")

    @commands.command(pass_context=True, name="messageLogging")
    @commands.check(administrator_perms)
    async def change_message_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends message logging messages in
        Usage: .messageLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["message"] != channel.id:
            Config.set_overwrite_logging_channel("message", channel)
            await ctx.send("Successfully updated message logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for message logging")

    @commands.command(pass_context=True, name="memberTracking")
    @commands.check(administrator_perms)
    async def change_member_tracking(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends member tracking messages in
        Usage: .messageLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["member_tracking"] != channel.id:
            Config.set_overwrite_logging_channel("member_tracking", channel)
            await ctx.send("Successfully updated member tracking channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for member tracking")

    @commands.command(pass_context=True, name="serverLogging")
    @commands.check(administrator_perms)
    async def change_server_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends voice logging messages in
        Usage: .serverLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["server"] != channel.id:
            Config.set_overwrite_logging_channel("server", channel)
            await ctx.send("Successfully updated server logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for server logging")

    @commands.command(pass_context=True, name="statusLogging")
    @commands.check(administrator_perms)
    async def change_status_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends status logging messages in
        Usage: .serverLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["status"] != channel.id:
            Config.set_overwrite_logging_channel("status", channel)
            await ctx.send("Successfully updated status logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for status logging")

    @commands.command(pass_context=True, name="voiceLogging")
    @commands.check(administrator_perms)
    async def change_voice_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends voice logging messages in
        Usage: .voiceLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.logging["overwrite_channels"]["voice"] != channel.id:
            Config.set_overwrite_logging_channel("voice", channel)
            await ctx.send("Successfully updated voice logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for voice logging")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Sends a logging message containing
        author, channel, content, and time of the deleted message
        :param message: message object deleted
        """
        if not message.author.bot:
            if Config.logging["overwrite_channels"]["message"] is not None:
                logging_channel = Config.logging["overwrite_channels"]["message"]
                channel = message.channel

                previous_message = await message.channel.history(limit=1, before=message.created_at).flatten()

                self.embed = discord.Embed(url=previous_message[0].jump_url)
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                entries = await message.guild.audit_logs(limit=1).flatten()

                self.embed.title = "Message deleted in " + "#" + channel.name
                if entries[0].action == discord.AuditLogAction.message_delete and entries[0].id != Config.logging["last_audit"]["last_audit"]:
                    user_id = entries[0].user.id
                    self.embed.description = message.content + "\n\n**Deleted by <@" + str(user_id) + ">**"
                    Config.set_last_audit = entries[0].id
                else:
                    self.embed.description = message.content

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        self.embed.add_field(name="Attachment", value=attachment.proxy_url)

                self.embed.set_footer(text="ID: " + str(message.author.id))
                self.embed.timestamp = datetime.utcnow()

                await logging_channel.send(embed=self.embed)

                if not entries[0].user.bot and entries[0].id != Config.logging["last_audit"]:
                    await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Sends a logging message containing
        location (channel), and ID of the message deleted
        :param payload:
        :return:
        """
        # If not a DM message
        if hasattr(payload, "guild_id"):
            guild = self.bot.get_guild(payload.guild_id)

            if Config.logging["overwrite_channels"]["message"] is not None and payload.cached_message is None:
                entries = await guild.audit_logs(limit=1).flatten()
                channel = guild.get_channel(payload.channel_id)

                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.title = "Message deleted in " + "#" + channel.name
                self.embed.set_footer(text="Uncached message: " + str(payload.message_id))
                self.embed.timestamp = datetime.utcnow()

                if entries[0].action == discord.AuditLogAction.message_delete and entries[0].id != Config.logging["last_audit"]:
                    user_id = entries[0].user.id
                    self.embed.description = "**Deleted by <@" + str(user_id) + ">**"
                    Config.set_last_audit = entries[0].id

                await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

                if not entries[0].user.bot and entries[0].id != Config.logging["last_audit"]:
                    await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        """
        Sends a logging message containing
        author, location (channel and placement), content, and time of the deleted messages
        May be limited if message is not in the cache
        :param payload:
        """
        # If not DM messages
        if hasattr(payload, "guild_id"):
            guild = self.bot.get_guild(payload.guild_id)

            if Config.logging["overwrite_channels"]["message"] is not None:
                channel = guild.get_channel(payload.channel_id)
                content = ""
                count = 0

                for message in payload.cached_messages:
                    count += 1
                    content += "[" + message.author.name + "#" + message.author.discriminator + "]: " + message.content + "\n"

                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.title = str(count) + " Messages bulk deleted in " + "#" + channel.name
                self.embed.description = content
                self.embed.timestamp = datetime.utcnow()

                await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)
                await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Sends a logging message containing
        the content of the message before and after the edit
        :param before: message object before
        :param after: message object after
        """
        if not before.author.bot:
            if Config.logging["overwrite_channels"]["message"] is not None:

                if before.content is after.content:
                    return

                channel = before.channel

                self.embed = discord.Embed(url=before.jump_url)
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=before.author.name + "#" + before.author.discriminator, icon_url=before.author.avatar_url)
                self.embed.title = "Message edited in #" + channel.name
                self.embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
                self.embed.set_footer(text="ID: " + str(before.author.id))
                self.embed.timestamp = datetime.utcnow()

                await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Sends a logging message containing
        the content of the message after the edit

        :param payload:
        :return:
        """
        # If a guild has been set
        if Config.guild is not None:
            # If not a DM message
            if Config.logging["overwrite_channels"]["message"] is not None and payload.cached_message is None:
                channel = Config.guild.get_channel(payload.channel_id)
                # If a dm message
                if channel is None:
                    return
                message = await channel.fetch_message(payload.message_id)

                if not message.author.bot:

                    self.embed = discord.Embed(url=message.jump_url)
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                    self.embed.title = "Message edited in #" + channel.name
                    self.embed.description = "**Uncached Message**\n**+After:** " + message.content
                    self.embed.set_footer(text="ID: " + str(message.author.id))
                    self.embed.timestamp = datetime.utcnow()

                    await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        :param channel:
        """
        if Config.logging["overwrite_channels"]["server"]is not None:
            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x43b581)
            permissions = ""

            # If a Category
            if channel.type is discord.ChannelType.category:
                self.embed.title = "Category created"
                description = "**Name:** " + channel.name + "\n**Position:** " + str(channel.position)

                if len(channel.overwrites) > 0:
                    for role in channel.overwrites:

                        # If you have permission to read messages
                        if channel.overwrites[role].pair()[0].read_messages is True:
                            permissions += "**Read Text Channels & See Voice Channels:** :white_check_mark:\n"
                            permissions += "**Connect:** :white_check_mark:"
                        else:
                            permissions += "**Read Text Channels & See Voice Channels:** :x:\n"
                            permissions += "**Connect:** :x:"

            else:
                description = "**Name:** " + channel.name + "\n**Position:** " + str(channel.position) + "\n**Category:** "
                if channel.category is not None:
                    description += channel.category.name
                else:
                    description += "None"

                # If a text channel
                if channel.type is discord.ChannelType.text:
                    self.embed.title = "Text channel created"

                    if len(channel.overwrites) > 0:
                        for role in channel.overwrites:
                            if channel.overwrites[role].pair()[0].read_messages is True:
                                permissions += "**Read messages:** :white_check_mark:"
                            else:
                                permissions += "**Read messages:** :x:"

                # If a VoiceChannel
                else:
                    self.embed.title = "Voice channel created"

                    if len(channel.overwrites) > 0:
                        for role in channel.overwrites:
                            permissions = ""
                            if channel.overwrites[role].pair()[0].connect is True:
                                permissions += "**Connect:** :white_check_mark:"
                            else:
                                permissions += "**Connect:** :x:"

            self.embed.add_field(name="Overwrites for " + str(role.name), value=permissions, inline=False)
            self.embed.description = description
            self.embed.set_footer(text="ID: " + str(channel.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        """
        if Config.logging["overwrite_channels"]["server"] is not None:
            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0xbe4041)

            if channel.type is discord.ChannelType.category:
                self.embed.title = "Category deleted"
                description = "**Name:** " + channel.name

            else:
                if channel.type is discord.ChannelType.text:
                    self.embed.title = "Text channel deleted"
                else:
                    self.embed.title = "Voice channel deleted"

                description = "**Name:** " + channel.name + "\n**Category:** "

                if channel.category is not None:
                    description += channel.category.name
                else:
                    description += "None"

            self.embed.description = description
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """
        Sends a logging message containing
        the updated properties of the channel
        """
        # Check name update
        if before.name != after.name:
            if before.type is discord.ChannelType.category:
                self.embed.title
        # Check position update
        # Check permission update
        # Slow mode
        # NSFW

        return

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        """
        Sends a logging message containing
        the name of the channel, the content of the pinned message, and a link to the message
        """
        return

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        """
        WTF are guild integrations???
        """
        return

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        """
        WTF are webhooks???
        """
        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, join position, account age
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            invites = await member.guild.invites()

            for invite in invites:
                if Config.logging["invites"][invite.code]["uses"] != invite.uses:
                    inviter_id = Config.logging["invites"][invite.code]["inviter_id"]
                    invite_code = invite.code
                    Config.update_invite(invite)

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.title = "Member joined"

            creation_delta = time_delta_string(member.created_at, datetime.utcnow())

            self.embed.description = "<@" + str(member.id) + "> " + make_ordinal(member.guild.member_count) + " to join\ncreated " + creation_delta + " ago\n\nInvite link created by <@" + str(inviter_id) + "> (" + invite_code + ")"
            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, time spent on the server
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)

            join_delta = time_delta_string(member.joined_at, datetime.utcnow())
            roles = ""

            for index in range(1, len(member.roles)):
                roles += "<@&" + str(member.roles[index].id) + "> "

            entries = await member.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.kick and entries[0].id != Config.logging["last_audit"]:
                Config.set_last_audit = entries[0].id
                self.embed.title = "Member kicked"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles + "\n\n**Kicked by <@" + str(entries[0].user.id) + ">**"
                if entries[0].reason is not None:
                    self.embed.description += "\n**Reason:** " + entries[0].reason

            else:
                self.embed.title = "Member left"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles

            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)

            if not entries[0].user.bot and entries[0].id != Config.logging["last_audit"]:
                await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Sends a logging message containing
        the property of the member updated before and after
        """

        # Check for role updates
        await self.role_update_checks(before, after)

        # Check for nickname updates
        await self.nickname_update_checks(before, after)

        # Check for status updates
        await self.status_update_checks(before, after)

    async def role_update_checks(self, before, after):
        """
        Checks for role updates and sends a member logging message if there are any

        :param before: Member object before
        :param after: Member object after
        """
        # Role checks
        added_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        # If roles edited and logging channel exists
        if len(added_roles) + len(removed_roles) > 0 and (Config.logging["channel"] is not None or Config.logging["overwrite_channels"]["mod"] is not None):

            # Reset embed
            self.embed = discord.Embed()
            self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)

            # Log who the editor is
            entries = await before.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.member_role_update:
                editor = "\n\nEdited by <@" + str(entries[0].user.id) + ">"

            if len(added_roles) > 0:

                # Roles have been added and removed
                if len(removed_roles) > 0:
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.title = "Roles updated"

                    self.embed.description = "**Added:** "
                    for role in added_roles:
                        self.embed.description += "<@&" + str(role.id) + "> "
                    self.embed.description += "\n**Removed:** "
                    for role in removed_roles:
                        self.embed.description += "<@&" + str(role.id) + "> "

                    self.embed.description += editor

                    self.embed.set_footer(text="ID: " + str(after.id))
                    self.embed.timestamp = datetime.utcnow()

                # Roles have only been added
                else:
                    self.embed.colour = discord.Colour(0x43b581)
                    if len(added_roles) > 1:
                        self.embed.title = "Roles added"
                    else:
                        self.embed.title = "Role added"
                    self.embed.description = ""
                    for role in added_roles:
                        self.embed.description += "<@&" + str(role.id) + "> "

                    self.embed.description += editor

                    self.embed.set_footer(text="ID: " + str(after.id))
                    self.embed.timestamp = datetime.utcnow()

            # Roles have only been removed
            else:
                self.embed.colour = discord.Colour(0xbe4041)
                if len(removed_roles) > 1:
                    self.embed.title = "Roles removed"
                else:
                    self.embed.title = "Role removed"
                self.embed.description = ""
                for role in removed_roles:
                    self.embed.description += "<@&" + str(role.id) + "> "

                self.embed.description += editor

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["member"].send(embed=self.embed)

            if not entries[0].user.bot and entries[0].id != Config.logging["last_audit"]:
                await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    async def nickname_update_checks(self, before, after):
        """
        Checks for nickname updates and sends a member logging message if there are any

        :param before: Member object before
        :param after: Member object after
        """
        # Nickname check
        if before.nick != after.nick:
            self.embed = discord.Embed()
            if before.nick is None:
                self.embed.title = "Nickname added"
                self.embed.description = "**Before: **\n**+After: **" + after.nick
                self.embed.colour = discord.Colour(0x43b581)
            elif after.nick is None:
                self.embed.title = "Nickname removed"
                self.embed.description = "**Before: **" + before.nick + "\n**+After: **"
                self.embed.colour = discord.Colour(0xbe4041)
            else:
                self.embed.title = "Nickname changed"
                self.embed.description = "**Before: **" + before.nick + "\n**+After: **" + after.nick
                self.embed.colour = discord.Colour(0x8899d4)

            self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
            self.embed.set_footer(text="ID: " + str(after.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["member"].send(embed=self.embed)

    async def status_update_checks(self, before, after):
        """
        Checks for status updates and sends a status logging message if there are any

        :param before: Member object before
        :param after: Member object after
        """
        if Config.logging["overwrite_channels"]["status"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["status"]

            statusBefore = ""
            statusAfter = ""

            # If they have a custom status
            if isinstance(after.activity, discord.CustomActivity):
                if after.activity.emoji is not None:
                    statusAfter += str(after.activity.emoji) + " "
                if after.activity.name is not None:
                    statusAfter += after.activity.name

                # If the user had a custom status before
                if isinstance(before.activity, discord.CustomActivity):
                    if before.activity.emoji is not None:
                        statusBefore += str(before.activity.emoji) + " "
                    if before.activity.name is not None:
                        statusBefore += before.activity.name

                    # If the status has changed
                    if statusAfter != statusBefore:
                        self.embed = discord.Embed()
                        self.embed.colour = discord.Colour(0x8899d4)
                        self.embed.title = "Custom status edited"
                    else:
                        statusBefore = ""
                        statusAfter = ""

                # If the user had a custom status stored from before
                elif str(after.id) in self.statuses:
                    statusBefore = self.statuses[str(after.id)]

                    # If the status has been updated
                    if statusAfter != statusBefore:
                        self.embed = discord.Embed()
                        self.embed.colour = discord.Colour(0x43b581)
                        self.embed.title = "Custom status added"

                        del self.statuses[str(after.id)]
                    else:
                        statusBefore = ""
                        statusAfter = ""
                # A status was added
                else:
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.title = "Custom status added"
            # If they had a custom status before and it is now gone
            elif isinstance(before.activity, discord.CustomActivity):
                if before.activity.emoji is not None:
                    statusBefore += str(before.activity.emoji) + " "
                if before.activity.name is not None:
                    statusBefore += before.activity.name

                # Store the status
                self.statuses[str(after.id)] = statusBefore
                statusBefore = ""

            if statusBefore != "" or statusAfter != "":
                self.embed.description = "**Before:** " + statusBefore + "\n**+After:** " + statusAfter
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()
                await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """
        Sends a logging message containing
        the property of the user updated before and after
        """
        if Config.logging["overwrite_channels"]["member"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["member"]

            # Check for avatar update
            if before.avatar != after.avatar:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Avatar update"
                self.embed.set_image(url=after.avatar_url)
                self.embed.description = "<@" + str(after.id) + ">"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                avatar_channel = Config.guild.get_channel(738536336016801793)
                await avatar_channel.send(embed=self.embed)

            # Check for name update
            elif before.name != after.name:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Name change"
                self.embed.description = "**Before:** " + before.name + "\n**+After:** " + after.name
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

            # Check for discriminator update
            elif before.discriminator != after.discriminator:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Discriminator update"
                self.embed.description = "**Before:** " + before.discriminator + "\n**+After:** " + after.discriminator
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """
        Sends a logging message containing
        the property of the guild updated before and after
        """
        return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        return

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """
        Sends a logging message containing
        the property of the role updated before and after
        """
        return

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """
        Sends a logging message containing
        the id, name, and picture of the emoji
        """
        return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Sends a logging message containing
        the id, name, and updated voice properties of the member
        """
        if Config.logging["overwrite_channels"]["voice"] is not None:
            logging_channel = member.guild.get_channel(int(Config.logging["overwrite_channels"]["voice"]))

            if before.channel is None:
                self.embed = discord.Embed()
                self.embed.title = "Member joined voice channel"
                self.embed.description = "**" + member.display_name + "** joined #" + after.channel.name
                self.embed.colour = discord.Colour(0x43b581)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()
                await logging_channel.send(embed=self.embed)

            elif after.channel is None:
                self.embed = discord.Embed()
                self.embed.title = "Member left voice channel"
                self.embed.description = "**" + member.display_name + "** left #" + before.channel.name
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()
                await logging_channel.send(embed=self.embed)

            elif before.channel.id != after.channel.id:
                self.embed = discord.Embed()
                self.embed.title = "Member changed voice channel"
                self.embed.description = "**Before: **#" + before.channel.name + "\n**+After: **#" + after.channel.name
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()
                await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """
        Sends a logging message containing
        the id, name, and join date of the member
        """
        if Config.logging["overwrite_channels"]["mod"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["mod"]
            entries = await guild.audit_logs(limit=1).flatten()
            Config.set_last_audit = entries[0].id

            self.embed = discord.Embed()
            self.embed.title = "Member banned"
            self.embed.description = "<@" + str(user.id) + ">\n\n**Banned by <@" + str(entries[0].user.id) + ">**"

            if entries[0].reason is not None:
                self.embed.description += "\n**Reason:** " + entries[0].reason

            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            self.embed.set_footer(text="ID: " + str(user.id))
            self.embed.timestamp = datetime.utcnow()

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """
        Sends a logging message containing
        the id and name of the member
        """
        if Config.logging["overwrite_channels"]["mod"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["mod"]

            self.embed = discord.Embed()
            self.embed.title = "Member unbanned"
            self.embed.description = "<@" + str(user.id) + ">"
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            self.embed.set_footer(text="ID: " + str(user.id))
            self.embed.timestamp = datetime.utcnow()

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """
        Sends a logging message containing
        the invite code, inviter name, inviter id, expiration time, invite max uses
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["member_tracking"]
            if invite.max_age == 0:
                expires = "Never"
            elif invite.max_age == 1800:
                expires = "30 minutes"
            elif invite.max_age == 3600:
                expires = "1 hour"
            elif invite.max_age == 21600:
                expires = "6 hours"
            elif invite.max_age == 43200:
                expires = "12 hours"
            else:
                expires = "1 day"

            Config.add_invite(invite.code, invite.inviter.id, invite.uses)
            self.embed = discord.Embed()
            self.embed.title = "Invite created to #" + invite.channel.name
            self.embed.description = "Code: " + invite.code + "\nMax Uses: " + str(invite.max_uses) + "\nExpires: " + expires + "\nTemporary Membership: " + str(invite.temporary) + "\n\n**Creator: <@" + str(invite.inviter.id) + ">**"
            self.embed.set_footer(text="ID: " + str(invite.inviter.id))
            self.embed.colour = discord.Colour(0x43b581)

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """
        Sends a logging message containing
        the invite code and moderator responsible for deleting it
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            logging_channel = Config.logging["overwrite_channels"]["member_tracking"]
            mod_log = Config.logging["overwrite_channels"]["mod"]

            entries = await invite.guild.audit_logs(limit=1).flatten()
            Config.set_last_audit = entries[0].id
            deleter = entries[0].user.id

            Config.remove_invite(invite.code)
            self.embed = discord.Embed()
            self.embed.title = "Invite deleted to #" + invite.channel.name
            self.embed.description = "Code: " + invite.code + "\n\n**Deleted by <@" + str(deleter) + ">**"
            self.embed.colour = discord.Colour(0xbe4041)

            await logging_channel.send(embed=self.embed)
            await mod_log.send(embed=self.embed)
