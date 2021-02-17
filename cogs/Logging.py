from cogs.Permissions import administrator_perms, moderator_perms
from GompeiFunctions import make_ordinal, time_delta_string
from discord.ext import commands
from datetime import timedelta
from datetime import datetime
from config import Config

import discord


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        if Config.guilds[channel.guild]["logging"]["channel"] != channel:
            # If logging has been disabled set all overwrites
            if Config.guilds[channel.guild]["logging"]["channel"] is None:
                Config.set_logging_channels(channel)
            else:
                Config.set_logging_channel(channel)

            await ctx.send("Successfully updated logging channel to <#" + str(channel.id) +
                           ">. If you'd like to set specific logging channels try using `" + Config.prefix +
                           "loggingOverwrite`.")
        else:
            await ctx.send("This channel is already being used for logging.")

    @commands.command(pass_context=True, name="loggingOverwrite")
    @commands.check(administrator_perms)
    async def change_overwrite_logging(self, ctx, overwrite: str, channel: discord.TextChannel):
        if overwrite.lower() in Config.guilds[channel.guild]["logging"]["overwrite_channels"]:
            if Config.guilds[channel.guild]["logging"]["overwrite_channels"][overwrite] != channel:
                Config.set_overwrite_logging_channel(overwrite.lower(), channel)
                await ctx.send("Successfully set " + overwrite.replace("_", " ").title() + " logging to " +
                               channel.mention)
            else:
                await ctx.send(overwrite.replace("_", " ").title() + " logging is already using " + channel.mention)
        else:
            overwrites = ""
            for overwrite in Config.guilds[channel.guild]["logging"]["overwrite_channels"].keys():
                overwrites = "`" + overwrite + "`\n"

            await ctx.send("The logging overwrite" + overwrite + " does not exist. The supported overwrites are:\n" +
                           overwrites)

    @commands.command(pass_context=True, name="memberLogging")
    @commands.check(administrator_perms)
    async def change_member_logging(self, ctx, channel: discord.TextChannel):
        """
        Changes the channel that the bot sends member logging messages in
        Usage: .memberLogging <channel>

        :param ctx: context object
        :param channel: channel ID or mention
        """
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["member"] != channel:
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
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["message"] != channel.id:
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
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["member_tracking"] != channel.id:
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
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["server"] != channel.id:
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
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["status"] != channel.id:
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
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["voice"] != channel.id:
            Config.set_overwrite_logging_channel("voice", channel)
            await ctx.send("Successfully updated voice logging channel to <#" + str(channel.id) + ">")
        else:
            await ctx.send("This channel is already being used for voice logging")

    @commands.command(pass_context=True, name="inviteNote")
    @commands.check(moderator_perms)
    async def invite_note(self, ctx, invite: discord.Invite, *, note: str):
        """
        Adds a note to an invite to be displayed on user join

        :param ctx: Context object
        :param invite: Invite to add note to
        :param note: Note to add
        """
        if invite in Config.guilds[ctx.guild]["logging"]["invites"]:
            Config.set_invite_note(invite, note)
            await ctx.send("Updated note for invite " + invite.code + " to:\n> " + note)
        else:
            Config.set_invite_note(invite, note)
            await ctx.send("Set note for invite " + invite.code + " to:\n> " + note)

    @commands.command(pass_context=True, name="removeInviteNote")
    @commands.check(moderator_perms)
    async def remove_invite_note(self, ctx, invite: discord.Invite):
        """
        Removes an invite note

        :param ctx: Context object
        :param invite: Invite to remove note from
        :param note: Note
        """
        if invite in Config.guilds[ctx.guild]["logging"]["invites"]:
            Config.remove_invite_note(invite)
            await ctx.send("Removed note for the invite")
        else:
            await ctx.send("This invite does not have a note")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Sends a logging message containing
        author, channel, content, and time of the deleted message

        :param message: message object deleted
        """
        if not message.author.bot:
            if Config.guilds[message.guild]["logging"]["overwrite_channels"]["message"] is not None:
                channel = message.channel

                previous_message = await message.channel.history(limit=1, before=message.created_at).flatten()

                embed = discord.Embed(
                    title="Message deleted in " + "#" + channel.name,
                    colour=discord.Colour(0xbe4041),
                    description=message.content
                )

                if previous_message[0] is not None:
                    embed.description += "\n[Previous Message](" + previous_message[0].jump_url + ")"

                if message.reference is not None: # Check for message reply
                    if message.reference.cached_message is None:
                        try:
                            message_reference = await message.guild.get_channel(message.reference.channel_id).fetch_message(message.reference.message_id)
                        except discord.NotFound:
                            if message.reference.message_id is None:  # Check if reply has been deleted
                                embed.description += "\nReplied to deleted message"
                    else:
                        message_reference = message.reference.cached_message

                    if message_reference.author in message.mentions \
                            and message_reference.author.mention not in message_reference.content:
                        name = "Reply mention to"
                    else:
                        name = "Reply to"

                    embed.add_field(
                        name=name,
                        value="https://discord.com/channels/" + str(message.reference.guild_id) + "/"
                              + str(message.reference.channel_id) + "/" + str(message.reference.message_id)
                    )

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        embed.add_field(name="Attachment", value=attachment.proxy_url)

                embed.set_author(
                    name=message.author.name + "#" + message.author.discriminator,
                    icon_url=message.author.avatar_url
                )
                embed.set_footer(text="ID: " + str(message.author.id))
                embed.timestamp = datetime.utcnow()

                entries = await message.guild.audit_logs(limit=1).flatten()
                if entries[0].action == discord.AuditLogAction.message_delete \
                        and entries[0].id != Config.guilds[message.guild]["logging"]["last_audit"]:
                    embed.description += "\n\n**Deleted by <@" + str(entries[0].user.id) + ">**"
                    Config.set_last_audit(entries[0])
                    if Config.guilds[message.guild]["logging"]["overwrite_channels"]["mod"] != \
                            Config.guilds[message.guild]["logging"]["overwrite_channels"]["message"]:
                        await self.send_embed(
                            embed,
                            Config.guilds[message.guild]["logging"]["overwrite_channels"]["mod"]
                        )

                await self.send_embed(embed, Config.guilds[message.guild]["logging"]["overwrite_channels"]["message"])

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Sends a logging message containing
        location (channel), and ID of the message deleted

        :param payload:
        """
        # If not a DM message
        if hasattr(payload, "guild_id"):
            guild = self.bot.get_guild(payload.guild_id)

            if Config.guilds[guild]["logging"]["overwrite_channels"]["message"] is not None and \
                    payload.cached_message is None:
                entries = await guild.audit_logs(limit=1).flatten()
                channel = guild.get_channel(payload.channel_id)

                embed = discord.Embed(
                    title="Message deleted in " + "#" + channel.name,
                    colour=discord.Colour(0xbe4041)
                )

                embed.set_footer(text="Uncached message: " + str(payload.message_id))
                embed.timestamp = datetime.utcnow()

                if entries[0].action == discord.AuditLogAction.message_delete \
                        and entries[0].id != Config.guilds[guild]["logging"]["last_audit"].id:
                    embed.description = "**Deleted by <@" + str(entries[0].user.id) + ">**"
                    Config.set_last_audit(entries[0])
                    if Config.guilds[guild]["logging"]["overwrite_channels"]["mod"] != \
                            Config.guilds[guild]["logging"]["overwrite_channels"]["message"]:
                        await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["mod"])

                await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["message"])

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

            if Config.guilds[guild]["logging"]["overwrite_channels"]["message"] is not None:
                channel = guild.get_channel(payload.channel_id)
                content = ""
                count = 0

                for message in payload.cached_messages:
                    count += 1
                    content += "[" + message.author.name + "#" + message.author.discriminator + "]: " + \
                               message.content + "\n"

                embed = discord.Embed(
                    title=str(count) + " Messages bulk deleted in " + "#" + channel.name,
                    colour=discord.Colour(0xbe4041),
                    description=content
                )

                embed.timestamp = datetime.utcnow()

                if Config.guilds[guild]["logging"]["overwrite_channels"]["mod"] != \
                        Config.guilds[guild]["logging"]["overwrite_channels"]["message"]:
                    await Config.guilds[guild]["logging"]["overwrite_channels"]["mod"].send(embed=embed)

                await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["message"])

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Sends a logging message containing
        the content of the message before and after the edit
        :param before: message object before
        :param after: message object after
        """
        if not before.author.bot:
            if Config.guilds[after.guild]["logging"]["overwrite_channels"]["message"] is not None:
                if before.pinned != after.pinned:
                    channel = after.channel

                    if after.pinned:
                        colour = discord.Colour(0x43b581)
                        title = "Message pinned in #" + channel.name
                    else:
                        colour = discord.Colour(0xbe4041)
                        title = "Message unpinned in #" + channel.name

                    embed = discord.Embed(
                        title=title,
                        colour=colour,
                        description=after.content
                    )

                    embed.description += "\n[Go To](" + after.jump_url + ")"

                    embed.set_author(
                        name=before.author.name + "#" + before.author.discriminator,
                        icon_url=before.author.avatar_url
                    )
                    embed.set_footer(text="ID: " + str(before.author.id))
                    embed.timestamp = datetime.utcnow()

                    await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["message"])

                else:
                    if before.content is after.content:
                        return

                    channel = before.channel

                    embed = discord.Embed(
                        title="Message edited in #" + channel.name,
                        colour=discord.Colour(0x8899d4),
                        description="**Before:** " + before.content + "\n**+After:** " + after.content
                    )

                    embed.description += "\n[Go To](" + after.jump_url + ")"

                    embed.set_author(
                        name=before.author.name + "#" + before.author.discriminator,
                        icon_url=before.author.avatar_url
                    )
                    embed.set_footer(text="ID: " + str(before.author.id))
                    embed.timestamp = datetime.utcnow()

                    await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["message"])

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Sends a logging message containing
        the content of the message after the edit

        :param payload:
        :return:
        """
        # If not DM messages
        if hasattr(payload, "guild_id"):
            guild = self.bot.get_guild(payload.guild_id)

            if Config.guilds[guild]["logging"]["overwrite_channels"]["message"] is not None and \
                    payload.cached_message is None:
                channel = Config.guild.get_channel(payload.channel_id)
                # If a dm message
                if channel is None:
                    return
                message = await channel.fetch_message(payload.message_id)

                if not message.author.bot:
                    embed = discord.Embed(
                        title="Message edited in #" + channel.name,
                        url=message.jump_url,
                        colour=discord.Colour(0x8899d4),
                        description="**Uncached Message**\n**+After:** " + message.content
                    )

                    embed.description += "\n[Go To](" + message.jump_url + ")"

                    embed.set_author(
                        name=message.author.name + "#" + message.author.discriminator,
                        icon_url=message.author.avatar_url
                    )
                    embed.set_footer(text="ID: " + str(message.author.id))
                    embed.timestamp = datetime.utcnow()

                    await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["message"])

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        :param channel:
        """
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["server"]is not None:
            permissions = ""

            # If a Category
            if channel.type is discord.ChannelType.category:
                title = "Category created"
                description = "**Name:** " + channel.name + "\n**Position:** " + str(channel.position)

            else:
                description = "**Name:** " + channel.name + "\n**Position:** " + str(channel.position) + \
                              "\n**Category:** "
                if channel.category is not None:
                    description += channel.category.name
                else:
                    description += "None"

                # If a text channel
                if channel.type is discord.ChannelType.text:
                    title = "Text channel created"

                    if len(channel.overwrites) > 0:
                        for role in channel.overwrites:
                            if channel.overwrites[role].pair()[0].read_messages is True:
                                permissions += "**Read messages:** :white_check_mark:"
                            else:
                                permissions += "**Read messages:** :x:"

                # If a VoiceChannel
                else:
                    title = "Voice channel created"

                    if len(channel.overwrites) > 0:
                        for role in channel.overwrites:
                            permissions = ""
                            if channel.overwrites[role].pair()[0].connect is True:
                                permissions += "**Connect:** :white_check_mark:"
                            else:
                                permissions += "**Connect:** :x:"

            embed = discord.Embed(
                title=title,
                colour=discord.Colour(0x43b581),
                description=description
            )

            embed.set_footer(text="ID: " + str(channel.id))
            embed.timestamp = datetime.utcnow()

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
                    field_description += permissions[i] + \
                                         (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
                field_description += "```"

                embed.add_field(name=target.name, value=field_description, inline=True)

            # Log who the editor is
            entries = await channel.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.channel_create \
                    and entries[0].id != Config.guilds[channel.guild]["logging"]["last_audit"]:
                Config.set_last_audit(entries[0])
                embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
            else:
                embed.description += "\n\nCreated by Discord"

            await self.send_embed(embed, Config.guilds[channel.guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        """
        if Config.guilds[channel.guild]["logging"]["overwrite_channels"]["server"] is not None:

            if channel.type is discord.ChannelType.category:
                title = "Category deleted"
                description = "**Name:** " + channel.name + "**Position:** " + str(channel.position)

            else:
                if channel.type is discord.ChannelType.text:
                    title = "Text channel deleted"
                else:
                    title = "Voice channel deleted"

                description = "**Name:** " + channel.name + "**Position:** " + str(channel.position) + \
                              "\n**Category:** "

                if channel.category is not None:
                    description += channel.category.name
                else:
                    description += "None"

            embed = discord.Embed(
                title=title,
                colour=discord.Colour(0xbe4041),
                description=description
            )

            embed.set_footer(text="ID: " + str(channel.id))
            embed.timestamp = datetime.utcnow()

            # Log who the editor is
            entries = await channel.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.channel_create \
                    and entries[0].id != Config.guilds[channel.guild]["logging"]["last_audit"]:
                Config.set_last_audit(entries[0])
                embed.description += "\n\nDeleted by <@" + str(entries[0].user.id) + ">"
            else:
                embed.description += "\n\nDeleted by Discord"

            await self.send_embed(embed, Config.guilds[channel.guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """
        Sends a logging message containing
        the updated properties of the channel
        """
        if Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"] is not None:
            embed = discord.Embed()
            embed.description = ""
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
                embed.description += "\n" + role.mention + " overwrites added"
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
                        field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + \
                                             values[i] + "\n"
                    field_description += "```"

            for role in removed_overwrites:
                embed.description += "\n" + role.mention + " overwrites removed"

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
                        field_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + \
                                             values[i] + "\n"
                    field_description += "```"

                    embed.add_field(name=key.name, value=field_description, inline=True)

            # If a text channel
            if isinstance(before, discord.TextChannel):
                embed.title = "Text Channel Updated"

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
                        before_value += "\n**Slowmode:** " + time_delta_string(
                            datetime.now(), datetime.now() + timedelta(seconds=before.slowmode_delay)
                        )
                    else:
                        before_value += "\n**Slowmode:** None"
                    if after.slowmode_delay > 0:
                        after_value += "\n**Slowmode:** " + time_delta_string(
                            datetime.now(), datetime.now() + timedelta(seconds=after.slowmode_delay)
                        )
                    else:
                        after_value += "\n**Slowmode:** None"

                # NSFW
                if before.is_nsfw() != after.is_nsfw():
                    before_value += "\n**NSFW:** " + str(before.is_nsfw())
                    after_value += "\n**NSFW:** " + str(after.is_nsfw())

            # If a voice channel
            elif isinstance(before, discord.VoiceChannel):
                embed.title = "Voice Channel Updated"

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
                embed.title = "Category Updated"

            if before_value != "":
                embed.add_field(name="Before", value=before_value, inline=True)
                embed.add_field(name="After", value=after_value, inline=True)
            embed.set_footer(text="ID: " + str(after.id))
            embed.colour = discord.Colour(0x8899d4)

            # Log who the editor is
            if entries[0].action == discord.AuditLogAction.channel_update \
                    and entries[0].id != Config.guilds[after.guild]["logging"]["last_audit"]:
                Config.set_last_audit(entries[0])
                embed.description += "\n\nUpdated by <@" + str(entries[0].user.id) + ">"

            if len(embed.description) > 0 or len(embed.fields) > 0:
                embed.description = after.mention + "\n" + embed.description
                await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, join position, account age
        """
        if Config.guilds[member.guild]["logging"]["overwrite_channels"]["member_tracking"] is not None:
            invites = await member.guild.invites()

            for invite in invites:
                if Config.guilds[member.guild]["logging"]["invites"][invite]["uses"] != invite.uses:
                    Config.update_invite_uses(invite)

                    creation_delta = time_delta_string(member.created_at, datetime.utcnow())

                    note = ""
                    if Config.guilds[member.guild]["logging"]["invites"][invite]["note"] is not None:
                        note = "\n**Note: **" + Config.guilds[member.guild]["logging"]["invites"][invite]["note"]

                    embed = discord.Embed(
                        title="Member joined",
                        colour=discord.Colour(0x43b581),
                        description=(
                            "<@" + str(member.id) + "> " + make_ordinal(member.guild.member_count) +
                            " to join\ncreated " + creation_delta + " ago\n\nInvite link created by <@" +
                            str(invite.inviter.id) + "> (" + invite.code + ")" + note
                        )
                    )

                    embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                    embed.set_footer(text="ID: " + str(member.id))
                    embed.timestamp = datetime.utcnow()

                    await self.send_embed(
                        embed,
                        Config.guilds[member.guild]["logging"]["overwrite_channels"]["member_tracking"]
                    )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, time spent on the server
        """
        if Config.guilds[member.guild]["logging"]["overwrite_channels"]["member_tracking"] is not None:
            embed = discord.Embed(colour=discord.Colour(0xbe4041))
            embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)

            join_delta = time_delta_string(member.joined_at, datetime.utcnow())
            roles = ""

            for index in range(1, len(member.roles)):
                roles += "<@&" + str(member.roles[index].id) + "> "

            embed.set_footer(text="ID: " + str(member.id))
            embed.timestamp = datetime.utcnow()

            entries = await member.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.kick and entries[0].id != \
                    Config.guilds[member.guild]["logging"]["last_audit"].id:
                Config.set_last_audit(entries[0])
                embed.title = "Member kicked"
                embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles + \
                                    "\n\n**Kicked by <@" + str(entries[0].user.id) + ">**"
                if entries[0].reason is not None:
                    embed.description += "\n**Reason:** " + entries[0].reason

                if Config.guilds[member.guild]["logging"]["overwrite_channels"]["mod"] \
                        != Config.guilds[member.guild]["logging"]["overwrite_channels"]["member_tracking"]:
                    await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["mod"])
            else:
                embed.title = "Member left"
                embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles

            await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["member_tracking"])

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
        if len(added_roles) + len(removed_roles) > 0 \
                and (Config.guilds[after.guild]["logging"]["channel"] is not None or
                     Config.guilds[after.guild]["logging"]["overwrite_channels"]["mod"] is not None):

            # Reset embed
            embed = discord.Embed()
            embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)

            if len(added_roles) > 0:

                # Roles have been added and removed
                if len(removed_roles) > 0:
                    embed.colour = discord.Colour(0x8899d4)
                    embed.title = "Roles updated"

                    embed.description = "**Added:** "
                    for role in added_roles:
                        embed.description += "<@&" + str(role.id) + "> "
                    embed.description += "\n**Removed:** "
                    for role in removed_roles:
                        embed.description += "<@&" + str(role.id) + "> "

                    embed.set_footer(text="ID: " + str(after.id))
                    embed.timestamp = datetime.utcnow()

                # Roles have only been added
                else:
                    embed.colour = discord.Colour(0x43b581)
                    if len(added_roles) > 1:
                        embed.title = "Roles added"
                    else:
                        embed.title = "Role added"
                    embed.description = ""
                    for role in added_roles:
                        embed.description += "<@&" + str(role.id) + "> "

                    embed.set_footer(text="ID: " + str(after.id))
                    embed.timestamp = datetime.utcnow()

            # Roles have only been removed
            else:
                embed.colour = discord.Colour(0xbe4041)
                if len(removed_roles) > 1:
                    embed.title = "Roles removed"
                else:
                    embed.title = "Role removed"
                embed.description = ""
                for role in removed_roles:
                    embed.description += "<@&" + str(role.id) + "> "

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

            # Log who the editor is
            entries = await before.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.member_role_update \
                    and entries[0].id != Config.guilds[after.guild]["logging"]["last_audit"]:
                Config.set_last_audit(entries[0])
                embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
                if not entries[0].user.bot and Config.guilds[after.guild]["logging"]["overwrite_channels"]["mod"] \
                        != Config.guilds[after.guild]["logging"]["overwrite_channels"]["member"]:
                    await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["mod"])
            else:
                embed.description = "\n\nEdited by Discord"

            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["member"])

    async def nickname_update_checks(self, before, after):
        """
        Checks for nickname updates and sends a member logging message if there are any

        :param before: Member object before
        :param after: Member object after
        """
        # Nickname check
        if before.nick != after.nick:

            embed = discord.Embed()
            if before.nick is None:
                embed.title = "Nickname added"
                embed.description = "**Before: **\n**+After: **" + after.nick
                embed.colour = discord.Colour(0x43b581)
            elif after.nick is None:
                embed.title = "Nickname removed"
                embed.description = "**Before: **" + before.nick + "\n**+After: **"
                embed.colour = discord.Colour(0xbe4041)
            else:
                embed.title = "Nickname changed"
                embed.description = "**Before: **" + before.nick + "\n**+After: **" + after.nick
                embed.colour = discord.Colour(0x8899d4)

            # Log who the editor is
            entries = await before.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.member_update \
                    and entries[0].id != Config.guilds[after.guild]["logging"]["last_audit"]:
                Config.set_last_audit(entries[0])
                if before != entries[0].user:
                    embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"

            embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
            embed.set_footer(text="ID: " + str(after.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["member"])

    async def status_update_checks(self, before, after):
        """
        Checks for status updates and sends a status logging message if there are any

        :param before: Member object before
        :param after: Member object after
        """
        if Config.guilds[after.guild]["logging"]["overwrite_channels"]["status"] is not None:

            status_before = ""
            status_after = ""
            links = ""

            # If they have a custom status
            if isinstance(after.activity, discord.CustomActivity):
                if after.activity.emoji is not None:
                    if after.activity.emoji.is_custom_emoji():
                        if after.activity.emoji.animated:
                            status_after += "\<a\:"
                        else:
                            status_after += "\<\:"

                        status_after += after.activity.emoji.name + ":" + str(after.activity.emoji.id) + "> "

                        links += "[Emoji After](" + str(after.activity.emoji.url) + ")\n"

                    else:
                        status_after += after.activity.emoji.name + " "
                if after.activity.name is not None:
                    status_after += after.activity.name

                # If the user had a custom status before
                if isinstance(before.activity, discord.CustomActivity):
                    if before.activity.emoji is not None:
                        if before.activity.emoji.is_custom_emoji():
                            if before.activity.emoji.animated:
                                status_before += "\<a\:"
                            else:
                                status_before += "\<\:"

                            status_before += before.activity.emoji.name + ":" + str(before.activity.emoji.id) + "> "
                            if before.activity.emoji == after.activity.emoji:
                                links = "[Emoji](" + str(before.activity.emoji.url) + ")"
                            else:
                                links = "[Emoji Before](" + str(before.activity.emoji.url) + ")\n" + links
                        else:
                            status_before += before.activity.emoji.name + " "
                    if before.activity.name is not None:
                        status_before += before.activity.name

                    # If the status has changed
                    if status_after != status_before:
                        embed = discord.Embed()
                        embed.colour = discord.Colour(0x8899d4)
                        embed.title = "Custom status edited"
                    else:
                        status_before = ""
                        status_after = ""

                # If the user had a custom status stored from before
                elif str(after.id) in self.statuses:
                    status_before = self.statuses[str(after.id)]

                    # If the status has been updated
                    if status_after != status_before:
                        embed = discord.Embed()
                        embed.colour = discord.Colour(0x8899d4)
                        embed.title = "Custom status edited"

                        del self.statuses[str(after.id)]
                    else:
                        status_before = ""
                        status_after = ""
                # A status was added
                else:
                    embed = discord.Embed()
                    embed.colour = discord.Colour(0x43b581)
                    embed.title = "Custom status added"

            # If they had a custom status before and it is now gone
            elif isinstance(before.activity, discord.CustomActivity):
                if before.activity.emoji is not None:
                    if before.activity.emoji is not None:
                        if before.activity.emoji.is_custom_emoji():
                            if before.activity.emoji.animated:
                                status_before += "\<a\:"
                            else:
                                status_before += "\<\:"

                            status_before += before.activity.emoji.name + ":" + str(before.activity.emoji.id) + "> "
                            links = "[Emoji Before](" + str(before.activity.emoji.url) + ")\n" + links
                        else:
                            status_before += before.activity.emoji.name + " "
                if before.activity.name is not None:
                    status_before += before.activity.name

                # Store the status
                self.statuses[str(after.id)] = status_before
                status_before = ""

            if status_after != "":
                Config.save_statuses(self.statuses)
                embed.description = "**Before:** " + status_before + "\n**+After:** " + status_after + "\n\n" + links
                embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["status"])

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """
        Sends a logging message containing
        the property of the user updated before and after
        """
        for guild in Config.guilds:
            if after in guild.members:
                if Config.guilds[guild]["logging"]["overwrite_channels"]["member"] is not None:

                    # Check for name update
                    if before.name != after.name:
                        embed = discord.Embed()
                        embed.colour = discord.Colour(0x8899d4)
                        embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                        embed.title = "Name change"
                        embed.description = "**Before:** " + before.name + "\n**+After:** " + after.name
                        embed.set_footer(text="ID: " + str(after.id))
                        embed.timestamp = datetime.utcnow()

                        await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["member"])

                    # Check for discriminator update
                    if before.discriminator != after.discriminator:
                        embed = discord.Embed()
                        embed.colour = discord.Colour(0x8899d4)
                        embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                        embed.title = "Discriminator update"
                        embed.description = "**Before:** " + before.discriminator + \
                                            "\n**+After:** " + after.discriminator
                        embed.set_footer(text="ID: " + str(after.id))
                        embed.timestamp = datetime.utcnow()

                        await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["member"])

                    # Check for avatar update
                    if Config.guilds[guild]["logging"]["overwrite_channels"]["avatar"] is not None:
                        if before.avatar != after.avatar:
                            embed = discord.Embed()
                            embed.colour = discord.Colour(0x8899d4)
                            embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                            embed.title = "Avatar update"
                            embed.set_image(url=after.avatar_url)
                            embed.description = "<@" + str(after.id) + ">"

                            embed.set_footer(text="ID: " + str(after.id))
                            embed.timestamp = datetime.utcnow()

                            await self.send_embed(
                                embed,
                                Config.guilds[guild]["logging"]["overwrite_channels"]["avatar"]
                            )

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """
        Sends a logging message containing
        the property of the guild updated before and after
        """
        if Config.guilds[after]["logging"]["overwrite_channels"]["server"] is not None:

            # AFK Channel / Timeout
            if before.afk_channel != after.afk_channel:
                if before.afk_channel is None:
                    title = "AFK Channel Added"
                    colour = discord.Colour(0x43b581)
                    description = "**Before:**\n**+After:** " + after.afk_channel.mention
                elif after.afk_channel is None:
                    title = "AFK Channel Removed"
                    colour = discord.Colour(0xbe4041)
                    description = "**Before:** " + before.afk_channel.mention + "\n**+After:** "
                else:
                    title = "AFK Channel Edited"
                    colour = discord.Colour(0x8899d4)
                    description = "**Before:** " + before.afk_channel.mention + "\n**+After:** " + \
                                  after.afk_channel.mention

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Notification Setting
            if before.default_notifications != after.default_notifications:
                embed = discord.Embed(
                    title="Default Notification Setting Changed",
                    colour=discord.Colour(0x8899d4),
                    description="**Before:** " + before.default_notifications + "\n**+After:** " +
                                after.default_notifications
                )

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Description
            if before.description != after.description:
                embed = discord.Embed()

                if before.description is None:
                    embed.title = "Description added"
                    embed.colour = discord.Colour(0x43b581)
                    embed.description = after.description
                elif after.description is None:
                    embed.title = "Description removed"
                    embed.colour = discord.Colour(0xbe4041)
                    embed.description = before.description
                else:
                    embed.title = "Description updated"
                    embed.colour = discord.Colour(0x8899d4)
                    embed.description = "***Before:** " + before.description + "\n**+After:** " + after.description

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Features
            if before.features != after.features:
                embed = discord.Embed()
                embed.title = "Features Edited"

                added_features = [x for x in after.features if x not in before.features]
                removed_features = [x for x in before.features if x not in after.features]

                if len(removed_features) == 0:
                    embed.colour = discord.Colour(0x43b581)
                    embed.description = "__Added Features__\n"
                    for feature in added_features:
                        embed.description += feature.replace("_", " ").title() + "\n"
                elif len(added_features) == 0:
                    embed.colour = discord.Colour(0xbe4041)
                    embed.description = "__Removed Features__\n"
                    for feature in removed_features:
                        embed.description += feature.replace("_", " ").title() + "\n"
                else:
                    embed.colour = discord.Colour(0x8899d4)
                    embed.description = "__Added Features__\n"
                    for feature in added_features:
                        embed.description += feature.replace("_", " ").title() + "\n"
                    embed.description += "\n__Removed Features__\n"
                    for feature in removed_features:
                        embed.description += feature.replace("_", " ").title() + "\n"

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # File Size Limit
            if before.filesize_limit != after.filesize_limit:
                embed = discord.Embed()

                if after.filesize_limit > before.filesize_limit:
                    embed.title = "Upload Limit Increased"
                    embed.colour = discord.Colour(0x43b581)
                    embed.description = str(after.filesize_limit / 1000000) + " MB"
                else:
                    embed.title = "Upload Limit Decreased"
                    embed.colour = discord.Colour(0xbe4041)
                    embed.description = str(after.filesize_limit / 1000000) + " MB"

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Emoji Limit
            if before.emoji_limit != after.emoji_limit:
                embed = discord.Embed()

                if after.emoji_limit > before.emoji_limit:
                    embed.title = "Emoji Limit Increased"
                    embed.colour = discord.Colour(0x43b581)
                    embed.description = str(after.emoji_limit) + " emojis"
                else:
                    embed.title = "Emoji Limit Decreased"
                    embed.colour = discord.Colour(0xbe4041)
                    embed.description = str(before.emoji_limit) + " emojis"

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # 2FA moderation
            if before.mfa_level != after.mfa_level:
                embed = discord.Embed()
                embed.title = "2FA Moderation Requirement"
                embed.colour = discord.Colour(0x8899d4)

                if after.mfa_level == 1:
                    embed.description = "True"
                else:
                    embed.description = "False"

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Owner
            if before.owner != after.owner:
                embed = discord.Embed()
                embed.title = "Server Owner Updated"
                embed.colour = discord.Colour(0x8899d4)
                embed.description = "**Before:** " + before.owner.mention + "\n" + "**+After:** " + after.owner.mention

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Name
            if before.name != after.name:
                embed = discord.Embed()
                embed.title = "Server Name Updated"
                embed.colour = discord.Colour(0x8899d4)
                embed.description = "**Before:** " + before.name + "\n" + "**+After:** " + after.name

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Public updates channel
            if before.public_updates_channel != after.public_updates_channel:
                if before.public_updates_channel is None:
                    title = "Public Updates Channel Added"
                    colour = discord.Colour(0x43b581)
                    description = after.public_updates_channel.mention
                elif after.public_updates_channel is None:
                    title = "Public Updates Channel Removed"
                    colour = discord.Colour(0xbe4041)
                    description = after.public_updates_channel.mention
                else:
                    title = "Public Updates Channel Updated"
                    colour = discord.Colour(0x8899d4)
                    description = "**Before:** " + before.public_updates_channel.mention + "**+After: " + \
                                  after.public_updates_channel.mention

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Rules channel
            if before.rules_channel != after.rules_channel:
                if before.rules_channel is None:
                    title = "Rules Channel Added"
                    colour = discord.Colour(0x43b581)
                    description = after.rules_channel.mention
                elif after.rules_channel is None:
                    title = "Rules Channel Removed"
                    colour = discord.Colour(0xbe4041)
                    description = after.rules_channel.mention
                else:
                    title = "Rules Channel Updated"
                    colour = discord.Colour(0x8899d4)
                    description = "**Before:** " + before.rules_channel.mention + "**+After: " + \
                                  after.rules_channel.mention

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Region
            if before.region != after.region:
                embed = discord.Embed()
                embed.title = "Region Updated"
                embed.colour = discord.Colour(0x8899d4)
                embed.description = str(after.region).replace("-", " ").title()

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # System Channel
            if before.system_channel != after.system_channel:
                if before.system_channel is None:
                    title = "System Channel Added"
                    colour = discord.Colour(0x43b581)
                    description = after.system_channel.mention
                elif after.rules_channel is None:
                    title = "System Channel Removed"
                    colour = discord.Colour(0xbe4041)
                    description = before.system_channel.mention
                else:
                    title = "System Channel Updated"
                    colour = discord.Colour(0x8899d4)
                    description = "**Before:** " + before.system_channel.mention + "**+After: " + \
                                  after.system_channel.mention

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Verification Level
            if before.verification_level != after.verification_level:
                embed = discord.Embed()
                embed.title = "Moderation Level Changed"
                embed.colour = discord.Colour(0x8899d4)
                embed.description = str(after.verification_level).title()
                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Banner
            if before.banner != after.banner:
                embed = discord.Embed()

                if before.banner is None:
                    embed.title = "Banner Added"
                    embed.colour = discord.Colour(0x43b581)
                    embed.set_image(url=after.banner_url)
                elif after.banner is None:
                    embed.title = "Banner Removed"
                    embed.colour = discord.Colour(0xbe4041)
                    embed.set_image(url=before.banner_url)
                else:
                    embed.title = "Banner Changed"
                    embed.colour = discord.Colour(0x8899d4)
                    embed.set_image(url=after.banner_url)

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Discovery Splash
            if before.discovery_splash != after.discovery_splash:
                embed = discord.Embed()
                embed.title = "Splash Changed"
                embed.colour = discord.Colour(0x8899d4)
                embed.set_image(url=after.discovery_splash_url)

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Icon
            if before.icon != after.icon:
                embed = discord.Embed()
                embed.title = "Server Icon Updated"
                embed.colour = discord.Colour(0x8899d4)
                embed.set_image(url=after.icon_url)
                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

            # Splash
            if before.splash != after.splash:
                embed = discord.Embed()

                if before.splash is None:
                    embed.title = "Invite Splash Added"
                    embed.colour = discord.Colour(0x43b581)
                    embed.set_image(url=after.splash_url)
                elif after.splash is None:
                    embed.title = "Invite Splash Removed"
                    embed.colour = discord.Colour(0xbe4041)
                    embed.set_image(url=before.splash_url)
                else:
                    embed.title = "Invite Splash Updated"
                    embed.colour = discord.Colour(0x8899d4)
                    embed.set_image(url=after.splash_url)

                embed.set_footer(text="ID: " + str(after.id))
                embed.timestamp = datetime.utcnow()

                await self.guild_update_helper(embed, after)
                await self.send_embed(embed, Config.guilds[after]["logging"]["overwrite_channels"]["server"])

    async def guild_update_helper(self, embed, guild: discord.Guild):
        entries = await guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.guild_update and \
                entries[0].id != Config.guilds[guild]["logging"]["last_audit"]:
            Config.set_last_audit(entries[0])
            embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
        else:
            embed.description += "\n\nEdited by Discord"

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        embed = discord.Embed(
            title="Role created",
            colour=discord.Colour(0x43b581),
            description=(
                    "**Name:** " + role.name +
                    "\n**Mention:** " + role.mention +
                    "\n**(R,G,B):** " + str(role.color.to_rgb()) +
                    "\n**Position:** " + str(role.position)
            )
        )

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

        embed.add_field(name="Permissions", value=permission_values, inline=True)

        if len(embed.description) > 2048:
            embed.description = embed.description[0:2047]

        embed.set_footer(text=str(role.id))
        embed.timestamp = datetime.utcnow()

        # Log who the editor is
        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_create and \
                entries[0].id != Config.guilds[role.guild]["logging"]["last_audit"]:
            Config.set_last_audit(entries[0])
            embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            embed.description += "\n\nCreated by Discord"

        await self.send_embed(embed, Config.guilds[role.guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """
        Sends a logging message containing
        the id, name, color, mentionable, and hoisted properties of the role
        """
        embed = discord.Embed(
            title="Role created",
            colour=discord.Colour(0xbe4041),
            description=(
                    "**Name:** " + role.name +
                    "\n**Mention:** " + role.mention +
                    "\n**(R,G,B):** " + str(role.color.to_rgb()) +
                    "\n**Position:** " + str(role.position)
            )
        )

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

        embed.add_field(name="Permissions", value=permission_values, inline=True)

        if len(embed.description) > 2048:
            embed.description = embed.description[0:2047]

        embed.set_footer(text=str(role.id))
        embed.timestamp = datetime.utcnow()

        # Log who the editor is
        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_delete and \
                entries[0].id != Config.guilds[role.guild]["logging"]["last_audit"]:
            Config.set_last_audit(entries[0])
            embed.description += "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            embed.description += "\n\nCreated by Discord"

        await self.send_embed(embed, Config.guilds[role.guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """
        Sends a logging message containing
        the property of the role updated before and after
        """
        # Name
        if before.name != after.name:
            embed = discord.Embed()
            embed.title = "Role Name Changed"
            embed.colour = discord.Colour(0x8899d4)
            embed.description = after.mention + "\n\n**Before:** " + before.name + "\n**+After:** " + after.name

            await self.role_update_helper(after, embed)
            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])

        # Colour
        if before.colour != after.colour:
            embed = discord.Embed(
                title="Role Color Changed",
                colour=discord.Colour(0x8899d4),
                description=(
                    after.mention +
                    "\n\n**Before:** " + str(before.color.to_rgb()) +
                    "\n**+After:** " + str(after.color.to_rgb())
                )
            )

            await self.role_update_helper(after, embed)
            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])
        
        # Hoisted
        if before.hoist != after.hoist:
            embed = discord.Embed(
                colour=discord.Colour(0x8899d4),
                description=after.mention
            )

            if before.hoist is False:
                embed.title = "Role Hoisted"
            else:
                embed.title = "Role Unhoisted"

            await self.role_update_helper(after, embed)
            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])

        # Mentionable
        if before.mentionable != after.mentionable:
            embed = discord.Embed(
                colour=discord.Colour(0x8899d4),
                description=after.mention
            )

            if before.mentionable is False:
                embed.title = "Role Made Mentionable"
            else:
                embed.title = "Role Made Unmentionable"

            await self.role_update_helper(after, embed)
            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])

        # Permissions
        if before.permissions != after.permissions:

            embed = discord.Embed(
                title="Role Permissions Edited",
                colour=discord.Colour(0x8899d4),
                description=after.mention
            )

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
                field_description += permissions[i] + \
                                     (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
            field_description += "```"

            embed.add_field(name="​", value=field_description, inline=True)
            await self.role_update_helper(after, embed)
            await self.send_embed(embed, Config.guilds[after.guild]["logging"]["overwrite_channels"]["server"])

    async def role_update_helper(self, role, embed):
        embed.set_footer(text=str(role.id))
        embed.timestamp = datetime.utcnow()

        entries = await role.guild.audit_logs(limit=1).flatten()
        if entries[0].action == discord.AuditLogAction.role_update and entries[0].id != \
                Config.guilds[role.guild]["logging"]["last_audit"]:
            Config.set_last_audit(entries[0])
            embed.description += "\n\nEdited by <@" + str(entries[0].user.id) + ">"
        else:
            embed.description += "\n\nEdited by Discord"

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """
        Sends a logging message containing
        the id, name, and picture of the emoji
        """
        # Log who the editor is
        entries = await guild.audit_logs(limit=1).flatten()
        if (entries[0].action == discord.AuditLogAction.emoji_create
            or entries[0].action == discord.AuditLogAction.emoji_delete) \
                and entries[0].id != Config.guilds[guild]["logging"]["last_audit"]:
            Config.set_last_audit(entries[0])
            editor = "\n\nCreated by <@" + str(entries[0].user.id) + ">"
        else:
            editor = "\n\nCreated by Discord"

        added_emojis = [x for x in after if x not in before]
        removed_emojis = [x for x in before if x not in after]

        for emoji in added_emojis:
            embed = discord.Embed(
                title="Emoji Added",
                colour=discord.Colour(0x43b581),
                description=emoji.name + editor
            )

            embed.set_image(url=emoji.url)
            embed.set_footer(text="ID: " + str(emoji.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["server"])

        for emoji in removed_emojis:
            embed = discord.Embed(
                title="Emoji Removed",
                colour=discord.Colour(0xbe4041),
                description=emoji.name + editor
            )

            embed.set_image(url=emoji.url)
            embed.set_footer(text="ID: " + str(emoji.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["server"])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Sends a logging message containing
        the id, name, and updated voice properties of the member
        """
        if Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"] is not None:
            # If voice channel was updated
            if before.channel != after.channel:
                if before.channel is None:
                    title = "Member joined voice channel"
                    colour = discord.Colour(0x43b581)
                    description = "**" + member.display_name + "** joined " + after.channel.mention
                elif after.channel is None:
                    title = "Member left voice channel"
                    colour = discord.Colour(0xbe4041)
                    description = "**" + member.display_name + "** left " + before.channel.mention
                else:
                    title = "Member changed voice channel"
                    description = "**Before: **#" + before.channel.name + "\n**+After: **" + after.channel.mention
                    colour = discord.Colour(0x8899d4)

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id))
                embed.timestamp = datetime.utcnow()

                entries = await member.guild.audit_logs(limit=1).flatten()
                if entries[0].action == discord.AuditLogAction.member_move and \
                        entries[0].id != Config.guilds[member.guild]["logging"]["last_audit"]:
                    Config.set_last_audit(entries[0])
                    embed.description += "\n\nMoved by <@" + str(entries[0].user.id) + ">"
                    if Config.guilds[member.guild]["logging"]["overwrite_channels"]["mod"] != Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"]:
                        await self.send_embed(
                            embed,
                            Config.guilds[member.guild]["logging"]["overwrite_channels"]["mod"]
                        )

                await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"])

            if before.self_stream != after.self_stream:
                if after.self_stream:
                    title = "Stream started"
                    colour = discord.Colour(0x43b581)
                else:
                    title = "Stream ended"
                    colour = discord.Colour(0xbe4041)

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description="**" + member.display_name + "** streaming in " + after.channel.mention
                )

                embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id))
                embed.timestamp = datetime.utcnow()

                await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"])

            if before.self_video != after.self_video:
                if after.self_video:
                    title = "Video started"
                    colour = discord.Colour(0x43b581)
                else:
                    title = "Video ended"
                    colour = discord.Colour(0xbe4041)

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description="**" + member.display_name + "** video in " + after.channel.mention
                )

                embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id))
                embed.timestamp = datetime.utcnow()

                await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"])

            if before.deaf != after.deaf:
                if after.deaf:
                    title = "Member server deafened"
                    colour = discord.Colour(0xbe4041)
                    description = "**" + member.display_name + "** deafened"
                else:
                    title = "Member server undeafened"
                    colour = discord.Colour(0x43b581)
                    description = "**" + member.display_name + "** undeafened"

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id))
                embed.timestamp = datetime.utcnow()

                await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"])

            if before.mute != after.mute:
                if after.mute:
                    title = "Member server muted"
                    colour = discord.Colour(0xbe4041)
                    description = "**" + member.display_name + "** muted"
                else:
                    title = "Member server unmuted"
                    colour = discord.Colour(0x43b581)
                    description = "**" + member.display_name + "** unmuted"

                embed = discord.Embed(
                    title=title,
                    colour=colour,
                    description=description
                )

                embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id))
                embed.timestamp = datetime.utcnow()

                await self.send_embed(embed, Config.guilds[member.guild]["logging"]["overwrite_channels"]["voice"])

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """
        Sends a logging message containing
        the id, name, and join date of the member
        """
        if Config.guilds[guild]["logging"]["overwrite_channels"]["mod"] is not None:
            entries = await guild.audit_logs(limit=1).flatten()
            Config.set_last_audit(entries[0])

            embed = discord.Embed(
                title="Member banned",
                colour=discord.Colour(0xbe4041),
                description="<@" + str(user.id) + ">\n\n**Banned by <@" + str(entries[0].user.id) + ">**"
            )

            if entries[0].reason is not None:
                embed.description += "\n**Reason:** " + entries[0].reason

            embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            embed.set_footer(text="ID: " + str(user.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["mod"])

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """
        Sends a logging message containing
        the id and name of the member
        """
        if Config.guilds[guild]["logging"]["overwrite_channels"]["mod"] is not None:

            embed = discord.Embed(
                title="Member unbanned",
                colour=discord.Colour(0x43b581),
                description="<@" + str(user.id) + ">"
            )

            embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
            embed.set_footer(text="ID: " + str(user.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(embed, Config.guilds[guild]["logging"]["overwrite_channels"]["mod"])

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """
        Sends a logging message containing
        the invite code, inviter name, inviter id, expiration time, invite max uses
        """
        if Config.guilds[invite.guild]["logging"]["overwrite_channels"]["member_tracking"] is not None:
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
            embed = discord.Embed(
                title="Invite created to #" + invite.channel.name,
                colour=discord.Colour(0x43b581),
                description=(
                        "Code: " + invite.code +
                        "\nMax Uses: " + str(invite.max_uses) +
                        "\nExpires: " + expires +
                        "\nTemporary Membership: " + str(invite.temporary) +
                        "\n\n**Creator: <@" + str(invite.inviter.id) + ">**"
                )
            )

            embed.set_footer(text="ID: " + str(invite.inviter.id))
            embed.timestamp = datetime.utcnow()

            await self.send_embed(
                embed,
                Config.guilds[invite.guild]["logging"]["overwrite_channels"]["member_tracking"]
            )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """
        Sends a logging message containing
        the invite code and moderator responsible for deleting it
        """
        if Config.guilds[invite.guild]["logging"]["overwrite_channels"]["member_tracking"] is not None:
            entries = await invite.guild.audit_logs(limit=1).flatten()
            Config.set_last_audit(entries[0])

            Config.remove_invite(invite)
            embed = discord.Embed(
                title="Invite deleted to #" + invite.channel.name,
                colour=discord.Colour(0xbe4041),
                description="Code: " + invite.code + "\n\n**Deleted by <@" + str(entries[0].id) + ">**"
            )

            if Config.guilds[invite.guild]["logging"]["overwrite_channels"]["mod"] != \
                    Config.guilds[invite.guild]["logging"]["overwrite_channels"]["member_tracking"]:
                await self.send_embed(embed, Config.guilds[invite.guild]["logging"]["overwrite_channels"]["mod"])

            await self.send_embed(
                embed,
                Config.guilds[invite.guild]["logging"]["overwrite_channels"]["member_tracking"]
            )

    async def send_embed(self, embed: discord.Embed, channel: discord.TextChannel):
        """
        Abstracts out embed sending to check for character limits

        :param embed: embed to send
        :param channel: channel to send to
        """
        content = embed.description
        title = embed.title
        if len(content) > 2048:
            chunks = []
            while len(content) > 0:
                chunk = content[: 2048]

                index = chunk.rfind("\n")
                if index == -1:
                    chunks.append(chunk)
                    content = content[2048:]
                else:
                    chunks.append(chunk[: index])
                    content = content[index + 1:]

            for i in range(0, len(chunks)):
                embed.description = chunks[i]
                embed.title = title + " (" + str(i + 1) + "/" + str(len(chunks)) + ")"
                await channel.send(embed=embed)
        else:
            await channel.send(embed=embed)

