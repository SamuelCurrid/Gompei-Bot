from GompeiFunctions import make_ordinal, time_delta_string, load_json, save_json, parse_id
from Permissions import administrator_perms
from discord.ext import commands
from datetime import datetime

import discord
import os


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_json(os.path.join("config", "settings.json"))
        self.embed = discord.Embed()
        self.logs = None
        self.statuses = None

    async def update_guilds(self):
        saved_guilds = []
        for guild_id in self.logs:
            saved_guilds.append(guild_id)

        guilds = []
        for guild in self.bot.guilds:
            guilds.append(str(guild.id))

        add_guilds = [x for x in guilds if x not in saved_guilds]
        remove_guilds = [x for x in saved_guilds if x not in guilds]

        # Add new guilds
        for guild_id in add_guilds:
            self.logs[str(guild_id)] = {"channel": None, "last_audit": None, "invites": None}

        # Remove disconnected guilds
        for guild_id in remove_guilds:
            self.logs.pop(str(guild_id))

        # Update invite links for guilds
        for guild_id in self.logs:
            guild = self.bot.get_guild(int(guild_id))
            invites = await guild.invites()
            cached_invites = {}

            for invite in invites:
                cached_invites[invite.code] = {"inviter_id": invite.inviter.id, "uses": invite.uses}

            self.logs[str(guild_id)]["invites"] = cached_invites

        save_json(os.path.join("config", "logging.json"), self.logs)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logs = load_json(os.path.join("config", "logging.json"))
        self.statuses = {}
        await self.update_guilds()

    @commands.command(pass_context=True, name="logging")
    @commands.check(administrator_perms)
    async def change_logging(self, ctx, arg1):
        """
        Changes the channel that the bot sends logging messages in
        :param ctx: context object
        :param arg1: channel ID or mention
        """
        channel = ctx.guild.get_channel(parse_id(arg1))

        if self.logs[str(ctx.message.guild.id)]["channel"] != channel.id:
            self.logs[str(ctx.message.guild.id)]["channel"] = channel.id

            save_json(os.path.join("config", "logging.json"), self.logs)
            await ctx.send("Successfully updated logging channel to <#" + str(channel.id) + ">")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Sends a logging message containing
        author, channel, content, and time of the deleted message
        :param message: message object deleted
        """
        if not message.author.bot:
            if self.logs[str(message.guild.id)]["channel"] is not None:
                logging_channel = message.guild.get_channel(int(self.logs[str(message.guild.id)]["channel"]))
                channel = message.channel

                previous_message = await message.channel.history(limit=1, before=message.created_at).flatten()

                self.embed = discord.Embed(url=previous_message[0].jump_url)
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                entries = await message.guild.audit_logs(limit=1).flatten()

                self.embed.title = "Message deleted in " + "#" + channel.name
                if entries[0].action == discord.AuditLogAction.message_delete and entries[0].id != self.logs[str(message.guild.id)]["last_audit"]:
                    user_id = entries[0].user.id
                    self.embed.description = message.content + "\n\n**Deleted by <@" + str(user_id) + ">**"
                    self.logs[str(message.guild.id)]["last_audit"] = entries[0].id
                    save_json(os.path.join("config", "logging.json"), self.logs)
                else:
                    self.embed.description = message.content

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        self.embed.add_field(name="Attachment", value=attachment.proxy_url)

                self.embed.set_footer(text="ID: " + str(message.author.id))
                self.embed.timestamp = datetime.utcnow()

                await logging_channel.send(embed=self.embed)

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

            if self.logs[str(guild.id)]["channel"] is not None and payload.cached_message is None:
                entries = await guild.audit_logs(limit=1).flatten()
                logging_channel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))
                channel = guild.get_channel(payload.channel_id)

                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.title = "Message deleted in " + "#" + channel.name
                self.embed.set_footer(text="Uncached message: " + str(payload.message_id))
                self.embed.timestamp = datetime.utcnow()

                if entries[0].action == discord.AuditLogAction.message_delete and entries[0].id != self.logs[str(guild.id)]["last_audit"]:
                    user_id = entries[0].user.id
                    self.embed.description = "**Deleted by <@" + str(user_id) + ">**"
                    self.logs[str(guild.id)]["last_audit"] = entries[0].id
                    save_json(os.path.join("config", "logging.json"), self.logs)

                await logging_channel.send(embed=self.embed)

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

            if self.logs[str(guild.id)]["channel"] is not None:

                logging_channel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))
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

                await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Sends a logging message containing
        the content of the message before and after the edit
        :param before: message object before
        :param after: message object after
        """
        if not before.author.bot:
            if self.logs[str(before.guild.id)]["channel"] is not None:

                if before.content is after.content:
                    return

                logging_channel = before.guild.get_channel(int(self.logs[str(before.guild.id)]["channel"]))
                channel = before.channel

                self.embed = discord.Embed(url=before.jump_url)
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=before.author.name + "#" + before.author.discriminator, icon_url=before.author.avatar_url)
                self.embed.title = "Message edited in #" + channel.name
                self.embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
                self.embed.set_footer(text="ID: " + str(before.author.id))
                self.embed.timestamp = datetime.utcnow()

                await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Sends a logging message containing
        the content of the message after the edit
        :param payload:
        :return:
        """
        # If not a DM message
        guild = self.bot.get_guild(self.settings["guild_id"])

        if self.logs[str(guild.id)]["channel"] is not None and payload.cached_message is None:
            channel = guild.get_channel(payload.channel_id)
            # If a dm message
            if channel is None:
                return
            message = await channel.fetch_message(payload.message_id)

            if not message.author.bot:
                logging_channel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))

                self.embed = discord.Embed(url=message.jump_url)
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                self.embed.title = "Message edited in #" + channel.name
                self.embed.description = "**Uncached Message**\n**+After:** " + message.content
                self.embed.set_footer(text="ID: " + str(message.author.id))
                self.embed.timestamp = datetime.utcnow()

                await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        :param channel:
        """
        if self.logs[str(channel.guild.id)]["channel"] is not None:
            logging_channel = channel.guild.get_channel(int(self.logs[str(channel.guild.id)]["channel"]))
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

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        """
        if self.logs[str(channel.guild.id)]["channel"] is not None:
            logging_channel = channel.guild.get_channel(int(self.logs[str(channel.guild.id)]["channel"]))
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
            await logging_channel.send(embed=self.embed)

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
        if self.logs[str(member.guild.id)]["channel"] is not None:
            logging_channel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))
            invites = await member.guild.invites()

            for invite in invites:
                if self.logs[str(member.guild.id)]["invites"][invite.code]["uses"] != invite.uses:
                    inviter_id = self.logs[str(member.guild.id)]["invites"][invite.code]["inviter_id"]
                    invite_code = invite.code
                    self.logs[str(member.guild.id)]["invites"][invite.code]["uses"] = invite.uses

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.title = "Member joined"

            creation_delta = time_delta_string(member.created_at, datetime.utcnow())

            self.embed.description = "<@" + str(member.id) + "> " + make_ordinal(member.guild.member_count) + " to join\ncreated " + creation_delta + " ago\n\nInvite link created by <@" + str(inviter_id) + "> (" + invite_code + ")"
            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, time spent on the server
        """
        if self.logs[str(member.guild.id)]["channel"] is not None:
            logging_channel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)

            join_delta = time_delta_string(member.joined_at, datetime.utcnow())
            roles = ""

            for index in range(1, len(member.roles)):
                roles += "<@&" + str(member.roles[index].id) + "> "

            entries = await member.guild.audit_logs(limit=1).flatten()
            if entries[0].action == discord.AuditLogAction.kick and entries[0].id != self.logs[str(member.guild.id)]["last_audit"]:
                self.logs[str(member.guild.id)]["last_audit"] = entries[0].id
                self.embed.title = "Member kicked"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles + "\n\n**Kicked by <@" + str(entries[0].user.id) + ">**"
                if entries[0].reason is not None:
                    self.embed.description += "\n**Reason:** " + entries[0].reason

            else:
                self.embed.title = "Member left"
                self.embed.description = "<@" + str(member.id) + "> joined " + join_delta + " ago\n**Roles: **" + roles

            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await logging_channel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Sends a logging message containing
        the property of the member updated before and after
        """

        if self.logs[str(after.guild.id)]["channel"] is not None:
            logging_channel = before.guild.get_channel(int(self.logs[str(after.guild.id)]["channel"]))

            # Role checks
            added_roles = [x for x in after.roles if x not in before.roles]
            removed_roles = [x for x in before.roles if x not in after.roles]

            # If roles edited
            if len(added_roles) + len(removed_roles) > 0:
                # Log who the editor is
                entries = await before.guild.audit_logs(limit=1).flatten()
                editor = ""
                if entries[0].action == discord.AuditLogAction.member_role_update:
                    editor += "\n\nEdited by <@" + str(entries[0].user.id) + ">"

                if len(added_roles) > 0:
                    # Roles have been added and removed
                    if len(removed_roles) > 0:
                        self.embed = discord.Embed()
                        self.embed.colour = discord.Colour(0x8899d4)
                        self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
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

                        await logging_channel.send(embed=self.embed)
                        return
                    else:
                        # Roles have only been added
                        self.embed = discord.Embed()
                        self.embed.colour = discord.Colour(0x43b581)
                        self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
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

                        await logging_channel.send(embed=self.embed)
                        return

                else:
                    # Roles have only been removed
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
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

                    await logging_channel.send(embed=self.embed)
                    return

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

                await logging_channel.send(embed=self.embed)

            statusBefore = ""
            statusAfter = ""
            # If user is coming online
            if before.raw_status == "offline":
                self.embed = discord.Embed()

                if str(after.id) in self.statuses:

                    # Custom status was removed
                    if not isinstance(after.activity, discord.CustomActivity):
                        self.embed.colour = discord.Colour(0xbe4041)
                        self.embed.title = "Custom status removed"
                        if self.statuses[str(after.id)]["emoji"] is not None:
                            statusBefore += self.statuses[str(after.id)]["emoji"] + " "
                        if self.statuses[str(after.id)]["name"] is not None:
                            statusBefore += self.statuses[str(after.id)]["name"]

                    # Custom status was edited
                    else:

                        self.embed.colour = discord.Colour(0x8899d4)
                        self.embed.title = "Custom status edited"

                        if after.activity.emoji != self.statuses[str(after.id)]["emoji"]:
                            statusBefore += self.statuses[str(after.id)]["emoji"] + " "
                            if after.activity.emoji is not None:
                                statusAfter += str(after.activity.emoji) + " "
                        if after.activity.name != self.statuses[str(after.id)]["name"]:
                            statusBefore += self.statuses[str(after.id)]["name"]
                            if after.activity.name is not None:
                                statusAfter += after.activity.name

                    del self.statuses[str(after.id)]

                # Custom status was added
                elif isinstance(after.activity, discord.CustomActivity):
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.title = "Custom status added"

                    if after.activity.emoji is not None:
                        statusAfter += str(after.activity.emoji) + " "
                    if after.activity.name is not None:
                        statusAfter += after.activity.name

            # Log custom statuses of those going offline
            elif after.raw_status == "offline":
                if isinstance(before.activity, discord.CustomActivity):

                    self.statuses[str(after.id)] = {"name": None, "emoji": None}

                    if before.activity.emoji is not None:
                        self.statuses[str(after.id)]["name"] = str(before.activity.emoji)
                    if before.activity.name is not None:
                        self.statuses[str(after.id)]["name"] = before.activity.name

            # Log custom status changes of those staying online
            elif isinstance(after.activity, discord.CustomActivity) or isinstance(before.activity, discord.CustomActivity):
                # Custom status was added
                if not isinstance(before.activity, discord.CustomActivity):
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0x43b581)
                    self.embed.title = "Custom status added"

                    if after.activity.emoji is not None:
                        statusAfter += str(after.activity.emoji) + " "
                    if after.activity.name is not None:
                        statusAfter += after.activity.name

                # Custom status was removed
                elif not isinstance(after.activity, discord.CustomActivity):
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.title = "Custom status removed"

                    if before.activity.emoji is not None:
                        statusBefore += str(before.activity.emoji) + " "
                    if before.activity.name is not None:
                        statusBefore += before.activity.name

                # Custom status was edited
                else:
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.title = "Custom status edited"

                    if before.activity.emoji is not None:
                        statusBefore += str(before.activity.emoji) + " "
                    if after.activity.emoji is not None:
                        statusAfter += str(after.activity.emoji) + " "
                    if before.activity.name is not None:
                        statusBefore += before.activity.name
                    if after.activity.name is not None:
                        statusAfter += after.activity.name

            if (statusBefore != "" or statusAfter != "") and statusBefore != statusAfter:
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
        if self.logs[str(self.settings["guild_id"])]["channel"] is not None:
            logging_channel = self.bot.get_guild(self.settings["guild_id"]).get_channel(int(self.logs[str(self.settings["guild_id"])]["channel"]))

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

                avatar_channel = self.bot.get_guild(self.settings["guild_id"]).get_channel(738536336016801793)
                await avatar_channel.send(embed=self.embed)
                return

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
        if self.logs[str(member.guild.id)]["channel"] is not None:
            logging_channel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))

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
        if self.logs[str(guild.id)]["channel"] is not None:
            logging_channel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))
            entries = await guild.audit_logs(limit=1).flatten()
            self.logs[str(guild.id)]["last_audit"] = entries[0].id

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
        if self.logs[str(guild.id)]["channel"] is not None:
            logging_channel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))

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
        if self.logs[str(invite.guild.id)]["channel"] is not None:
            logging_channel = invite.guild.get_channel(int(self.logs[str(invite.guild.id)]["channel"]))
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

            self.logs[str(invite.guild.id)]["invites"][invite.code] = {"inviter_id": invite.inviter.id, "uses": invite.uses}
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
        if self.logs[str(invite.guild.id)]["channel"] is not None:
            logging_channel = invite.guild.get_channel(int(self.logs[str(invite.guild.id)]["channel"]))
            entries = await invite.guild.audit_logs(limit=1).flatten()
            self.logs[str(invite.guild.id)]["last_audit"] = entries[0].id
            deleter = entries[0].user.id

            self.logs[str(invite.guild.id)]["invites"].pop(invite.code)
            self.embed = discord.Embed()
            self.embed.title = "Invite deleted to #" + invite.channel.name
            self.embed.description = "Code: " + invite.code + "\n\n**Deleted by <@" + str(deleter) + ">**"
            self.embed.colour = discord.Colour(0xbe4041)

            await logging_channel.send(embed=self.embed)
