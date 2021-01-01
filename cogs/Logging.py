from GompeiFunctions import make_ordinal, time_delta_string
from cogs.Permissions import administrator_perms
from discord.ext import commands
from datetime import timedelta
from datetime import datetime

import discord
from config import Config


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = discord.Embed()
        self.statuses = Config.load_statuses()

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

            # If logging has been disabled set all overwrites
            if Config.logging["channel"] is None:
                Config.set_logging_channels(channel)
            else:
                Config.set_logging_channel(channel)

            await ctx.send("Successfully updated logging channel to <#" + str(channel.id) + ">. If you'd like to set specific logging channels try using `" + Config.prefix + "loggingOverwrite`.")
        else:
            await ctx.send("This channel is already being used for logging.")

    @commands.command(pass_context=True, name="loggingOverwrite")
    @commands.check(administrator_perms)
    async def change_overwrite_logging(self, ctx, overwrite: str, channel: discord.TextChannel):
        if overwrite.lower() in Config.logging["overwrite_channels"]:
            if Config.logging["overwrite_channels"][overwrite] != channel:
                Config.set_overwrite_logging_channel(overwrite.lower(), channel)
                await ctx.send("Successfully set " + overwrite.replace("_", " ").title() + " logging to " + channel.mention)
            else:
                await ctx.send(overwrite.replace("_", " ").title() + " logging is already using " + channel.mention)
        else:
            overwrites = ""
            for overwrite in Config.logging["overwrite_channels"].keys():
                overwrites = "`" + overwrite + "`\n"

            await ctx.send("The logging overwrite" + overwrite + " does not exist. The supported overwrites are:\n" + overwrites)

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
                channel = message.channel

                previous_message = await message.channel.history(limit=1, before=message.created_at).flatten()

                self.embed = discord.Embed(url=previous_message[0].jump_url)
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                entries = await message.guild.audit_logs(limit=1).flatten()

                self.embed.title = "Message deleted in " + "#" + channel.name
                if entries[0].action == discord.AuditLogAction.message_delete and entries[0] != Config.logging["last_audit"]:
                    self.embed.description = message.content + "\n\n**Deleted by <@" + str(entries[0].user.id) + ">**"
                    Config.set_last_audit(entries[0])

                    if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["message"]:
                        await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)
                else:
                    self.embed.description = message.content

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        self.embed.add_field(name="Attachment", value=attachment.proxy_url)

                self.embed.set_footer(text="ID: " + str(message.author.id))
                self.embed.timestamp = datetime.utcnow()

                await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

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

                if entries[0].action == discord.AuditLogAction.message_delete and entries[0] != Config.logging["last_audit"].id:
                    self.embed.description = "**Deleted by <@" + str(entries[0].user.id) + ">**"
                    Config.set_last_audit(entries[0])
                    if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["message"]:
                        await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

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

                if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["message"]:
                    await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

                await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

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
                if before.pinned != after.pinned:
                    channel = after.channel
                    self.embed = discord.Embed(url=after.jump_url)

                    if after.pinned:
                        self.embed.colour = discord.Colour(0x43b581)
                        self.embed.title = "Message pinned in #" + channel.name
                    else:
                        self.embed.colour = discord.Colour(0xbe4041)
                        self.embed.title = "Message unpinned in #" + channel.name

                    self.embed.set_author(name=before.author.name + "#" + before.author.discriminator, icon_url=before.author.avatar_url)
                    self.embed.description = after.content
                    self.embed.set_footer(text="ID: " + str(before.author.id))
                    self.embed.timestamp = datetime.utcnow()
                    await Config.logging["overwrite_channels"]["message"].send(embed=self.embed)

                else:
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

            for target in channel.overwrites:
                permissions = []
                values = []

                for permission in channel.overwrites[target]:
                    if permission[1] is not None:
                        permissions.append(permission[0].replace("_", " ").title())
                        if permission[1] is True:
                            values.append("✔")
                        else:
                            values.append("✘")

                max_length = len(max(permissions, key=len))

                field_description = "```"
                for i in range(0, len(permissions)):
                    field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
                field_description += "```"

                self.embed.add_field(name=target.name, value=field_description, inline=True)

            # Log who the editor is
            entries = await channel.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.channel_create and entries[0] != Config.logging["last_audit"]:
                Config.set_last_audit(entries[0])
                self.embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
            else:
                self.embed.description  += "\n\nCreated by Discord"

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
                description = "**Name:** " + channel.name + "**Position:** " + channel.position

            else:
                if channel.type is discord.ChannelType.text:
                    self.embed.title = "Text channel deleted"
                else:
                    self.embed.title = "Voice channel deleted"

                description = "**Name:** " + channel.name + "**Position:** " + channel.position + "\n**Category:** "

                if channel.category is not None:
                    description += channel.category.name
                else:
                    description += "None"

            self.embed.description = description

            # Log who the editor is
            entries = await channel.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.channel_create and entries[0] != Config.logging["last_audit"]:
                Config.set_last_audit(entries[0])
                self.embed.description += "\n\nDeleted by <@" + str(entries[0].user.id) + ">"
            else:
                self.embed.description += "\n\nDeleted by Discord"

            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """
        Sends a logging message containing
        the updated properties of the channel
        """
        if Config.logging["overwrite_channels"]["server"] is not None:
            self.embed = discord.Embed()
            self.embed.description = ""
            before_value = ""
            after_value = ""

            entries = await after.guild.audit_logs(limit=1).flatten()

            # Check name update
            if before.name != after.name:
                before_value += "**Name:** " + before.name
                after_value += "**Name:** " + after.name

            # Check permission update
            added_overwrites = [x for x in after.overwrites if x not in before.overwrites]
            removed_overwrites = [x for x in before.overwrites if x not in after.overwrites]

            for role in added_overwrites:
                self.embed.description += "\n" + role.mention + " overwrites added"
                permissions = []
                values = []
                for permission in after.overwrites[role]:
                    if permission[1] is not None:
                        permissions.append(permission[0].replace("_", " ").title())
                        if permission[1] is True:
                            values.append("✔")
                        else:
                            values.append("✘")

                if len(permissions) != 0:
                    max_length = len(max(permissions, key=len))

                    field_description = "```"
                    for i in range(0, len(permissions)):
                        field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
                    field_description += "```"

            for role in removed_overwrites:
                self.embed.description += "\n" + role.mention + " overwrites removed"

            kept_overwrites = [x for x in after.overwrites if x in before.overwrites]

            for key in kept_overwrites:
                if before.overwrites[key] != after.overwrites[key]:
                    # Compare permissions
                    edited_permissions = [x for x in after.overwrites[key] if x not in before.overwrites[key]]
                    permissions = []
                    values = []
                    for perm in edited_permissions:
                        permissions.append(perm[0].replace("_", " ").title())
                        if perm[1] is True:
                            values.append("✔")
                        elif perm[1] is False:
                            values.append("✘")
                        else:
                            values.append("-")

                    max_length = len(max(permissions, key=len))

                    field_description = "```"
                    for i in range(0, len(permissions)):
                        field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
                    field_description += "```"

                    self.embed.add_field(name=key.name, value=field_description, inline=True)

            # If a text channel
            if isinstance(before, discord.TextChannel):
                self.embed.title = "Text Channel Updated"

                # Category
                if before.category != after.category:
                    before_value += "\n**Category:** " + str(before.category)
                    after_value += "\n**Category:** " + str(after.category)

                # Topic
                if before.topic != after.topic:
                    before_value += "\n**__Description__**```" + str(before.topic) + "```"
                    after_value += "\n**__Description__**```" + str(after.topic) + "```"

                # Slow mode
                if before.slowmode_delay != after.slowmode_delay:
                    if before.slowmode_delay > 0:
                        before_value += "\n**Slowmode:** " + time_delta_string(datetime.now(), datetime.now() + timedelta(seconds=before.slowmode_delay))
                    else:
                        before_value += "\n**Slowmode:** None"
                    if after.slowmode_delay > 0:
                        after_value += "\n**Slowmode:** " + time_delta_string(datetime.now(), datetime.now() + timedelta(seconds=after.slowmode_delay))
                    else:
                        after_value += "\n**Slowmode:** None"

                # NSFW
                if before.is_nsfw() != after.is_nsfw():
                    before_value += "\n**NSFW:** " + str(before.is_nsfw())
                    after_value += "\n**NSFW:** " + str(after.is_nsfw())

            # If a voice channel
            elif isinstance(before, discord.VoiceChannel):
                self.embed.title = "Voice Channel Updated"

                # Category
                if before.category != after.category:
                    before_value += "\n**Category:** " + str(before.category)
                    after_value += "\n**Category:** " + str(after.category)

                # Bitrate
                if before.bitrate != after.bitrate:
                    before_value += "\n**Bitrate:** " + str(before.bitrate)
                    after_value += "\n**Bitrate:** " + str(after.bitrate)

                # User limit
                if before.user_limit != after.user_limit:
                    before_value += "\n**Max Users:** " + str(before.user_limit)
                    after_value += "\n**Max Users:** " + str(after.user_limit)

            # If a category
            else:
                self.embed.title = "Category Updated"

            if before_value != "":
                self.embed.add_field(name="Before", value=before_value, inline=True)
                self.embed.add_field(name="After", value=after_value, inline=True)
            self.embed.set_footer(text="ID: " + str(after.id))
            self.embed.colour = discord.Colour(0x8899d4)

            # Log who the editor is
            if entries[0].action == discord.AuditLogAction.channel_update and entries[0] != Config.logging["last_audit"]:
                Config.set_last_audit(entries[0])
                self.embed.description += "\n\nUpdated by <@" + str(entries[0].user.id) + ">"

            if len(self.embed.description) > 0 or len(self.embed.fields) > 0:
                self.embed.description = after.mention + "\n" + self.embed.description
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, join position, account age
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            invites = await member.guild.invites()

            for invite in invites:
                if Config.logging["invites"][invite]["uses"] != invite.uses:
                    Config.update_invite_uses(invite)

                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                    self.embed.title = "Member joined"

                    creation_delta = time_delta_string(member.created_at, datetime.utcnow())

                    self.embed.description = "<@" + str(member.id) + "> " + make_ordinal(member.guild.member_count) + " to join\ncreated " + creation_delta + " ago\n\nInvite link created by <@" + str(invite.inviter.id) + "> (" + invite.code + ")"
                    self.embed.set_footer(text="ID: " + str(member.id))
                    self.embed.timestamp = datetime.utcnow()

                    await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)
                    return

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

            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            entries = await member.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.kick and entries[0] != Config.logging["last_audit"].id:
                Config.set_last_audit(entries[0])
                self.embed.title = "Member kicked"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles + "\n\n**Kicked by <@" + str(entries[0].user.id) + ">**"
                if entries[0].reason is not None:
                    self.embed.description += "\n**Reason:** " + entries[0].reason

                if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed):
                    await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)
            else:
                self.embed.title = "Member left"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles

            await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)

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

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

            # Log who the editor is
            entries = await before.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.member_role_update and entries[0] != Config.logging["last_audit"]:
                Config.set_last_audit(entries[0])
                self.embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
                if not entries[0].user.bot and Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["member"]:
                    await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)
            else:
                self.embed.description = "\n\nEdited by Discord"

            await Config.logging["overwrite_channels"]["member"].send(embed=self.embed)

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

            # Log who the editor is
            entries = await before.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.member_update and entries[0] != Config.logging["last_audit"]:
                Config.set_last_audit(entries[0])
                if before != entries[0].user:
                    self.embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"

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
                        self.embed.colour = discord.Colour(0x8899d4)
                        self.embed.title = "Custom status edited"

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
                Config.save_statuses(self.statuses)
                self.embed.description = "**Before:** " + statusBefore + "\n**+After:** " + statusAfter
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await Config.logging["overwrite_channels"]["status"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """
        Sends a logging message containing
        the property of the user updated before and after
        """
        if Config.logging["overwrite_channels"]["member"] is not None:

            # Check for name update
            if before.name != after.name:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Name change"
                self.embed.description = "**Before:** " + before.name + "\n**+After:** " + after.name
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()
                await Config.logging["overwrite_channels"]["member"].send(embed=self.embed)

            # Check for discriminator update
            if before.discriminator != after.discriminator:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Discriminator update"
                self.embed.description = "**Before:** " + before.discriminator + "\n**+After:** " + after.discriminator
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()
                await Config.logging["overwrite_channels"]["member"].send(embed=self.embed)

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

                await Config.logging["overwrite_channels"]["avatar"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """
        Sends a logging message containing
        the property of the guild updated before and after
        """
        if Config.logging["overwrite_channels"]["server"] is not None:

            # AFK Channel / Timeout
            if before.afk_channel != after.afk_channel:
                self.embed = discord.Embed()

                if before.afk_channel is None:
                    self.embed.title = "AFK Channel Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = "**Before:**\n**+After:** " + after.afk_channel.mention
                elif after.afk_channel is None:
                    self.embed.title = "AFK Channel Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = "**Before:** " + before.afk_channel.mention + "\n**+After:** "
                else:
                    self.embed.title = "AFK Channel Edited"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "**Before:** " + before.afk_channel.mention + "\n**+After:** " + after.afk_channel.mention

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Notification Setting
            if before.default_notifications != after.default_notifications:
                self.embed = discord.Embed()

                self.embed.title = "Default Notification Setting Changed"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.description = "**Before:** " + before.default_notifications + "\n**+After:** " + after.default_notifications

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Description
            if before.description != after.description:
                self.embed = discord.Embed()

                if before.description is None:
                    self.embed.title = "Description added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = after.description
                elif after.description is None:
                    self.embed.title = "Description removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = before.description
                else:
                    self.embed.title = "Description updated"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "***Before:** " + before.description + "\n**+After:** " + after.description

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Features
            if before.features != after.features:
                self.embed = discord.Embed()
                self.embed.title = "Features Edited"

                added_features = [x for x in after.features if x not in before.features]
                removed_features = [x for x in before.features if x not in after.features]

                if len(removed_features) == 0:
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = "__Added Features__\n"
                    for feature in added_features:
                        self.embed.description += feature.replace("_", " ").title() + "\n"
                elif len(added_features) == 0:
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = "__Removed Features__\n"
                    for feature in removed_features:
                        self.embed.description += feature.replace("_", " ").title() + "\n"
                else:
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "__Added Features__\n"
                    for feature in added_features:
                        self.embed.description += feature.replace("_", " ").title() + "\n"
                    self.embed.description += "\n__Removed Features__\n"
                    for feature in removed_features:
                        self.embed.description += feature.replace("_", " ").title() + "\n"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)


            # File Size Limit
            if before.filesize_limit != after.filesize_limit:
                self.embed = discord.Embed()

                if after.filesize_limit > before.filesize_limit:
                    self.embed.title = "Upload Limit Increased"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = str(after.filesize_limit / 1000000) + " MB"
                else:
                    self.embed.title = "Upload Limit Decreased"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = str(after.filesize_limit / 1000000) + " MB"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Emoji Limit
            if before.emoji_limit != after.emoji_limit:
                self.embed = discord.Embed()

                if after.emoji_limit > before.emoji_limit:
                    self.embed.title = "Emoji Limit Increased"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = str(after.emoji_limit) + " emojis"
                else:
                    self.embed.title = "Emoji Limit Decreased"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = str(before.emoji_limit) + " emojis"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # 2FA moderation
            if before.mfa_level != after.mfa_level:
                self.embed = discord.Embed()
                self.embed.title = "2FA Moderation Requirement"
                self.embed.colour = discord.Colour(0x8899d4)

                if after.mfa_level == 1:
                    self.embed.description = "True"
                else:
                    self.embed.description = "False"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Owner
            if before.owner != after.owner:
                self.embed = discord.Embed()
                self.embed.title = "Server Owner Updated"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.description = "**Before:** " + before.owner.mention + "\n" + "**+After:** " + after.owner.mention

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Name
            if before.name != after.name:
                self.embed = discord.Embed()
                self.embed.title = "Server Name Updated"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.description = "**Before:** " + before.name + "\n" + "**+After:** " + after.name

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Public updates channel
            if before.public_updates_channel != after.public_updates_channel:
                self.embed = discord.Embed()

                if before.public_updates_channel is None:
                    self.embed.title = "Public Updates Channel Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = after.public_updates_channel.mention
                elif after.public_updates_channel is None:
                    self.embed.title = "Public Updates Channel Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = after.public_updates_channel.mention
                else:
                    self.embed.title = "Public Updates Channel Updated"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "**Before:** " + before.public_updates_channel.mention + "**+After: " + after.public_updates_channel.mention

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Rules channel
            if before.rules_channel != after.rules_channel:
                self.embed = discord.Embed()

                if before.rules_channel is None:
                    self.embed.title = "Rules Channel Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = after.rules_channel.mention
                elif after.rules_channel is None:
                    self.embed.title = "Rules Channel Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = after.rules_channel.mention
                else:
                    self.embed.title = "Rules Channel Updated"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "**Before:** " + before.rules_channel.mention + "**+After: " + after.rules_channel.mention

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Region
            if before.region != after.region:
                self.embed = discord.Embed()
                self.embed.title = "Region Updated"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.description = str(after.region).replace("-", " ").title()

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # System Channel
            if before.system_channel != after.system_channel:
                self.embed = discord.Embed()

                if before.system_channel is None:
                    self.embed.title = "System Channel Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.description = after.system_channel.mention
                elif after.rules_channel is None:
                    self.embed.title = "System Channel Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.description = before.system_channel.mention
                else:
                    self.embed.title = "System Channel Updated"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.description = "**Before:** " + before.system_channel.mention + "**+After: " + after.system_channel.mention

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Verification Level
            if before.verification_level != after.verification_level:
                self.embed = discord.Embed()
                self.embed.title = "Moderation Level Changed"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.description = str(after.verification_level).title()
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Banner
            if before.banner != after.banner:
                self.embed = discord.Embed()

                if before.banner is None:
                    self.embed.title = "Banner Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.set_image(url=after.banner_url)
                elif after.banner is None:
                    self.embed.title = "Banner Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.set_image(url=before.banner_url)
                else:
                    self.embed.title = "Banner Changed"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.set_image(url=after.banner_url)

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Discovery Splash
            if before.discovery_splash != after.discovery_splash:
                self.embed = discord.Embed()
                self.embed.title = "Splash Changed"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_image(url=after.discovery_splash_url)

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Icon
            if before.icon != after.icon:
                self.embed = discord.Embed()
                self.embed.title = "Server Icon Updated"
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_image(url=after.icon_url)
                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

            # Splash
            if before.splash != after.splash:
                self.embed = discord.Embed()

                if before.splash is None:
                    self.embed.title = "Invite Splash Added"
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.set_image(url=after.splash_url)
                elif after.splash is None:
                    self.embed.title = "Invite Splash Removed"
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.set_image(url=before.splash_url)
                else:
                    self.embed.title = "Invite Splash Updated"
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.set_image(url=after.splash_url)

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    async def guild_update_helper(self, guild: discord.Guild):
        entries = await guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.guild_update and entries[0] != Config.logging["last_audit"]:
            Config.set_last_audit(entries[0])
            self.embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
        else:
            self.embed.description += "\n\nEdited by Discord"

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        self.embed = discord.Embed()
        self.embed.title = "Role created"
        self.embed.description = "**Name:** " + role.name
        self.embed.description += "\n**Mention:** " + role.mention
        self.embed.description += "\n**(R,G,B):** " + str(role.color.to_rgb())
        self.embed.description += "\n**Position:** " + str(role.position)
        self.embed.colour = discord.Colour(0x43b581)

        permissions = []
        values = []

        for permission in role.permissions:
            if permission[1] is not None:
                if permission[1] is True:
                    permissions.append(permission[0].replace("_", " ").title())
                    values.append("✔")

        max_length = len(max(permissions, key=len))

        permission_values = "```"
        for i in range(0, len(permissions)):
            permission_values += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
        permission_values += "```"

        self.embed.add_field(name="Permissions", value=permission_values, inline=True)

        if len(self.embed.description) > 2048:
            self.embed.description = self.embed.description[0:2047]

        self.embed.set_footer(text=str(role.id))
        self.embed.timestamp = datetime.utcnow()

        # Log who the editor is
        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_create and entries[0] != Config.logging["last_audit"]:
            Config.set_last_audit(entries[0])
            self.embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            self.embed.description += "\n\nCreated by Discord"

        await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        self.embed = discord.Embed()
        self.embed.title = "Role created"
        self.embed.description = "**Name:** " + role.name
        self.embed.description += "\n**Mention:** " + role.mention
        self.embed.description += "\n**(R,G,B):** " + str(role.color.to_rgb())
        self.embed.description += "\n**Position:** " + str(role.position)
        self.embed.colour = discord.Colour(0xbe4041)

        permissions = []
        values = []

        for permission in role.permissions:
            if permission[1] is not None:
                if permission[1] is True:
                    permissions.append(permission[0].replace("_", " ").title())
                    values.append("✔")

        max_length = len(max(permissions, key=len))

        permission_values = "```"
        for i in range(0, len(permissions)):
            permission_values += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
        permission_values += "```"

        self.embed.add_field(name="Permissions", value=permission_values, inline=True)

        if len(self.embed.description) > 2048:
            self.embed.description = self.embed.description[0:2047]

        self.embed.set_footer(text=str(role.id))
        self.embed.timestamp = datetime.utcnow()

        # Log who the editor is
        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_delete and entries[0] != Config.logging["last_audit"]:
            Config.set_last_audit(entries[0])
            self.embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            self.embed.description += "\n\nCreated by Discord"

        await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """
        Sends a logging message containing
        the property of the role updated before and after
        """
        # Name
        if before.name != after.name:
            self.embed = discord.Embed()
            self.embed.title = "Role Name Changed"
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.description = after.mention + "\n\n**Before:** " + before.name + "\n**+After:** " + after.name

            await self.role_update_helper(after)
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

        # Colour
        if before.colour != after.colour:
            self.embed = discord.Embed()
            self.embed.title = "Role Color Changed"
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.description = after.mention + "\n\n**Before:** " + str(before.color.to_rgb()) + "\n**+After:** " + str(after.color.to_rgb())

            await self.role_update_helper(after)
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)
        
        # Hoisted
        if before.hoist != after.hoist:
            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.description = after.mention

            if before.hoist is False:
                self.embed.title = "Role Hoisted"
            else:
                self.embed.title = "Role Unhoisted"

            await self.role_update_helper(after)
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

        # Mentionable
        if before.mentionable != after.mentionable:
            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.description = after.mention

            if before.mentionable is False:
                self.embed.title = "Role Made Mentionable"
            else:
                self.embed.title = "Role Made Unmentionable"

            await self.role_update_helper(after)
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

        # Permissions
        if before.permissions != after.permissions:

            self.embed = discord.Embed()
            self.embed.title = "Role Permissions Edited"
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.description = after.mention
            edited_perms = [x for x in after.permissions if x not in before.permissions]

            permissions = []
            values = []

            for perm in edited_perms:
                permissions.append(perm[0].replace("_", " ").title())
                if perm[1] is True:
                    values.append("✔")
                else:
                    values.append("-")

            max_length = len(max(permissions, key=len))

            field_description = "```"
            for i in range(0, len(permissions)):
                field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
            field_description += "```"

            self.embed.add_field(name="​", value=field_description, inline=True)
            await self.role_update_helper(after)
            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    async def role_update_helper(self, role):
        self.embed.set_footer(text=str(role.id))
        self.embed.timestamp = datetime.utcnow()

        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_update and entries[0] != Config.logging["last_audit"]:
            Config.set_last_audit(entries[0])
            self.embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
        else:
            self.embed.description += "\n\nEdited by Discord"

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """
        Sends a logging message containing
        the id, name, and picture of the emoji
        """
        self.embed = discord.Embed()

        # Log who the editor is
        entries = await guild.audit_logs(limit=1).flatten()
        if (entries[0].action == discord.AuditLogAction.emoji_create or entries[0].action == discord.AuditLogAction.emoji_delete) and entries[0] != Config.logging["last_audit"]:
            Config.set_last_audit(entries[0])
            editor = "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            editor = "\n\nCreated by Discord"

        added_emojis = [x for x in after if x not in before]
        removed_emojis = [x for x in before if x not in after]

        self.embed.colour = discord.Colour(0x43b581)
        self.embed.title = "Emoji Added"
        for emoji in added_emojis:
            self.embed.description = emoji.name + editor
            self.embed.set_image(url=emoji.url)
            self.embed.set_footer(text="ID: " + str(emoji.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

        self.embed.colour = discord.Colour(0xbe4041)
        self.embed.title = "Emoji Removed"
        for emoji in removed_emojis:
            self.embed.description = emoji.name + editor
            self.embed.set_image(url=emoji.url)
            self.embed.set_footer(text="ID: " + str(emoji.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["server"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Sends a logging message containing
        the id, name, and updated voice properties of the member
        """
        if Config.logging["overwrite_channels"]["voice"] is not None:

            if before.channel is None:
                self.embed = discord.Embed()
                self.embed.title = "Member joined voice channel"
                self.embed.description = "**" + member.display_name + "** joined #" + after.channel.name
                self.embed.colour = discord.Colour(0x43b581)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()

            elif after.channel is None:
                self.embed = discord.Embed()
                self.embed.title = "Member left voice channel"
                self.embed.description = "**" + member.display_name + "** left #" + before.channel.name
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()

                entries = await member.guild.audit_logs(limit=1).flatten()
                if entries[0].action == discord.AuditLogAction.member_disconnect and entries[0] != Config.logging["last_audit"] and entries[0].user != member:
                    Config.set_last_audit(entries[0])
                    self.embed.description += "\n\nDisconnected by <@" + str(entries[0].user.id) + ">"
                    if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["voice"]:
                        await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

            elif before.channel.id != after.channel.id:
                self.embed = discord.Embed()
                self.embed.title = "Member changed voice channel"
                self.embed.description = "**Before: **#" + before.channel.name + "\n**+After: **#" + after.channel.name
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                self.embed.set_footer(text="ID: " + str(member.id))
                self.embed.timestamp = datetime.utcnow()

                entries = await member.guild.audit_logs(limit=1).flatten()
                if entries[0].action == discord.AuditLogAction.member_move and entries[0] != Config.logging["last_audit"]:
                    Config.set_last_audit(entries[0])
                    self.embed.description += "\n\nMoved by <@" + str(entries[0].user.id) + ">"
                    if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["voice"]:
                        await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

            await Config.logging["overwrite_channels"]["voice"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """
        Sends a logging message containing
        the id, name, and join date of the member
        """
        if Config.logging["overwrite_channels"]["mod"] is not None:
            entries = await guild.audit_logs(limit=1).flatten()
            Config.set_last_audit(entries[0])

            self.embed = discord.Embed()
            self.embed.title = "Member banned"
            self.embed.description = "<@" + str(user.id) + ">\n\n**Banned by <@" + str(entries[0].user.id) + ">**"

            if entries[0].reason is not None:
                self.embed.description += "\n**Reason:** " + entries[0].reason

            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            self.embed.set_footer(text="ID: " + str(user.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """
        Sends a logging message containing
        the id and name of the member
        """
        if Config.logging["overwrite_channels"]["mod"] is not None:

            self.embed = discord.Embed()
            self.embed.title = "Member unbanned"
            self.embed.description = "<@" + str(user.id) + ">"
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            self.embed.set_footer(text="ID: " + str(user.id))
            self.embed.timestamp = datetime.utcnow()

            await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """
        Sends a logging message containing
        the invite code, inviter name, inviter id, expiration time, invite max uses
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
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

            Config.add_invite(invite)
            self.embed = discord.Embed()
            self.embed.title = "Invite created to #" + invite.channel.name
            self.embed.description = "Code: " + invite.code + "\nMax Uses: " + str(invite.max_uses) + "\nExpires: " + expires + "\nTemporary Membership: " + str(invite.temporary) + "\n\n**Creator: <@" + str(invite.inviter.id) + ">**"
            self.embed.set_footer(text="ID: " + str(invite.inviter.id))
            self.embed.colour = discord.Colour(0x43b581)

            await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """
        Sends a logging message containing
        the invite code and moderator responsible for deleting it
        """
        if Config.logging["overwrite_channels"]["member_tracking"] is not None:
            entries = await invite.guild.audit_logs(limit=1).flatten()
            Config.set_last_audit(entries[0])

            Config.remove_invite(invite)
            self.embed = discord.Embed()
            self.embed.title = "Invite deleted to #" + invite.channel.name
            self.embed.description = "Code: " + invite.code + "\n\n**Deleted by <@" + str(entries[0].id) + ">**"
            self.embed.colour = discord.Colour(0xbe4041)

            if Config.logging["overwrite_channels"]["mod"] != Config.logging["overwrite_channels"]["member_tracking"]:
                await Config.logging["overwrite_channels"]["mod"].send(embed=self.embed)

            await Config.logging["overwrite_channels"]["member_tracking"].send(embed=self.embed)

