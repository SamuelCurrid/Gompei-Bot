from GompeiFunctions import make_ordinal
from Permissions import command_channels
from dateutil import relativedelta
from discord.ext import commands
from datetime import datetime

import discord
import json
import os


def parse_id(arg):
    """
    Parses an ID from a discord mention
    :param arg: mention or ID passed
    :return: ID
    """
    if "<" in arg:
        for i, c in enumerate(arg):
            if c.isdigit():
                return int(arg[i:-1])
    # Using ID
    else:
        return int(arg)


def timeDeltaString(date1, date2):
    """
    Returns a string with three most significant time deltas between date1 and date2
    :param date1: datetime 1
    :param date2: datetime 2
    :return: string
    """
    delta = relativedelta.relativedelta(date2, date1)

    if delta.years > 0:
        if delta.years == 1:
            output = str(delta.years) + " year, "
        else:
            output = str(delta.years) + " years, "
        if delta.months == 1:
            output += str(delta.months) + " month, "
        else:
            output += str(delta.months) + " months, "

        if delta.days == 1:
            output += "and " + str(delta.days) + " day"
        else:
            output += "and " + str(delta.days) + " days"

        return output

    elif delta.months > 0:
        if delta.months == 1:
            output = str(delta.months) + " month, "
        else:
            output = str(delta.months) + " months, "
        if delta.days == 1:
            output += str(delta.days) + " day, "
        else:
            output += str(delta.days) + " days, "
        if delta.hours == 1:
            output += "and " + str(delta.hours) + " hour"
        else:
            output += "and " + str(delta.hours) + " hours"

        return output

    elif delta.days > 0:
        if delta.days == 1:
            output = str(delta.days) + " day, "
        else:
            output = str(delta.days) + " days, "
        if delta.hours == 1:
            output += str(delta.hours) + " hour, "
        else:
            output += str(delta.hours) + " hours, "
        if delta.minutes == 1:
            output += "and " + str(delta.minutes) + " minute"
        else:
            output += "and " + str(delta.minutes) + " minutes"

        return output

    elif delta.hours > 0:
        if delta.hours == 1:
            output = str(delta.hours) + " hour, "
        else:
            output = str(delta.hours) + " hours, "
        if delta.minutes == 1:
            output += str(delta.minutes) + " minute, "
        else:
            output += str(delta.minutes) + " minutes, "
        if delta.seconds == 1:
            output += "and " + str(delta.seconds) + " second"
        else:
            output += "and " + str(delta.seconds) + " seconds"

        return output

    elif delta.minutes > 0:
        if delta.minutes == 1:
            output = str(delta.minutes) + " minute "
        else:
            output = str(delta.minutes) + " minutes "
        if delta.seconds == 1:
            output += "and " + str(delta.seconds) + " second"
        else:
            output += "and " + str(delta.seconds) + " seconds"

        return output

    elif delta.seconds > 0:
        if delta.seconds == 1:
            return str(delta.seconds) + " second"
        else:
            return str(delta.seconds) + " seconds"

    return "!!DATETIME ERROR!!"


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = discord.Embed()
        self.logs = None

    async def update_guilds(self):
        savedGuilds = []
        for guildID in self.logs:
            savedGuilds.append(guildID)

        guilds = []
        for guild in self.bot.guilds:
            guilds.append(str(guild.id))

        addGuilds = [x for x in guilds if x not in savedGuilds]
        removeGuilds = [x for x in savedGuilds if x not in guilds]

        # Add new guilds
        for guildID in addGuilds:
            self.logs[str(guildID)] = {"channel": None}

        # Remove disconnected guilds
        for guildID in removeGuilds:
            self.logs.pop(str(guildID))

        await self.update_state()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_state()
        await self.update_guilds()

    @commands.command(pass_context=True, name="logging")
    @commands.check(command_channels)
    async def change_logging(self, ctx, arg1):
        """
        Changes the channel that the bot sends logging messages in
        :param ctx: context object
        :param arg1: channel ID or mention
        """
        channel = ctx.guild.get_channel(parse_id(arg1))
        print(parse_id(arg1))

        if self.logs[str(ctx.message.guild.id)]["channel"] != channel.id:
            self.logs[str(ctx.message.guild.id)]["channel"] = channel.id

            print("Updating guild " + str(ctx.message.guild.id) + " to use logging channel " + str(channel.id))

            await self.update_state()
            print("Finished updating logging channel")
            await ctx.send("Successfully updated logging channel to <#" + str(channel.id) + ">")

    @change_logging.error
    async def change_logging_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print("!ERROR! " + str(ctx.author.id) + " did not have permissions for change logging command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command is missing arguments")
        else:
            print(error)

    async def load_state(self):
        with open(os.path.join("config", "logging.json"), "r+") as loggingFile:
            logs = loggingFile.read()
            self.logs = json.loads(logs)

    async def update_state(self):
        with open(os.path.join("config", "logging.json"), "r+") as loggingFile:
            loggingFile.truncate(0)
            loggingFile.seek(0)
            json.dump(self.logs, loggingFile, indent=4)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Sends a logging message containing
        author, channel, content, and time of the deleted message
        :param message: message object deleted
        """
        if not message.author.bot:
            if self.logs[str(message.guild.id)]["channel"] is not None:
                loggingChannel = message.guild.get_channel(int(self.logs[str(message.guild.id)]["channel"]))
                channel = message.channel

                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0xbe4041)
                self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                self.embed.title = "Message deleted in " + "#" + channel.name
                self.embed.description = message.content

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        self.embed.add_field(name="Attachment", value=attachment.proxy_url)

                self.embed.set_footer(text="ID: " + str(message.author.id))
                self.embed.timestamp = datetime.utcnow()

                await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Sends a logging message containing
        location (channel), and ID of the message deleted
        :param payload:
        :return:
        """
        guild = self.bot.get_guild(payload.guild_id)

        if self.logs[str(guild.id)]["channel"] is not None and payload.cached_message is None:
            loggingChannel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))
            channel = guild.get_channel(payload.channel_id)

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.title = "Message deleted in " + "#" + channel.name
            self.embed.set_footer(text="Uncached message: " + str(payload.message_id))
            self.embed.timestamp = datetime.utcnow()

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        """
        Sends a logging message containing
        author, location (channel and placement), content, and time of the deleted messages
        May be limited if message is not in the cache
        :param payload:
        """
        guild = self.bot.get_guild(payload.guild_id)

        if self.logs[str(guild.id)]["channel"] is not None:

            loggingChannel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))
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

            await loggingChannel.send(embed=self.embed)

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

                loggingChannel = before.guild.get_channel(int(self.logs[str(before.guild.id)]["channel"]))
                channel = before.channel

                self.embed = discord.Embed(url=before.jump_url)
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=before.author.name + "#" + before.author.discriminator, icon_url=before.author.avatar_url)
                self.embed.title = "Message edited in #" + channel.name
                self.embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
                self.embed.set_footer(text="ID: " + str(before.author.id))
                self.embed.timestamp = datetime.utcnow()

                await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Sends a logging message containing
        the content of the message after the edit
        :param payload:
        :return:
        """
        guild = self.bot.get_guild(payload.guild_id)

        if self.logs[str(guild.id)]["channel"] is not None and payload.cached_message is None:
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            loggingChannel = guild.get_channel(int(self.logs[str(guild.id)]["channel"]))

            self.embed = discord.Embed(url=message.jump_url)
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
            self.embed.title = "Message edited in #" + channel.name
            self.embed.description = "**Uncached Message**\n**+After:** " + message.content
            self.embed.set_footer(text="ID: " + str(message.author.id))
            self.embed.timestamp = datetime.utcnow()

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        :param channel:
        """
        if self.logs[str(channel.guild.id)]["channel"] is not None:
            loggingChannel = channel.guild.get_channel(int(self.logs[str(channel.guild.id)]["channel"]))
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
                description = "**Name:** " + channel.name + "\n**Position:** " + str(
                    channel.position) + "\n**Category:** "
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

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """
        Sends a logging message containing
        the name, category, and permissions of the channel
        """
        if self.logs[str(channel.guild.id)]["channel"] is not None:
            loggingChannel = channel.guild.get_channel(int(self.logs[str(channel.guild.id)]["channel"]))
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
            await loggingChannel.send(embed=self.embed)

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
            loggingChannel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.title = "Member joined"

            creationDelta = timeDeltaString(member.created_at, datetime.utcnow())

            self.embed.description = "<@" + str(member.id) + "> " + make_ordinal(member.guild.member_count) + " to join\ncreated " + creationDelta + " ago"
            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Sends a logging message containing
        the name, avatar, id, time spent on the server
        """
        if self.logs[str(member.guild.id)]["channel"] is not None:
            loggingChannel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))

            self.embed = discord.Embed()
            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.title = "Member left"

            joinDelta = timeDeltaString(member.joined_at, datetime.utcnow())
            roles = ""

            for index in range(1, len(member.roles)):
                roles += "<@&" + str(member.roles[index].id) + "> "

            self.embed.description = "<@" + str(member.id) + "> joined " + joinDelta + " ago\n**Roles: **" + roles
            self.embed.set_footer(text="ID: " + str(member.id))
            self.embed.timestamp = datetime.utcnow()

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Sends a logging message containing
        the property of the member updated before and after
        """
        loggingChannel = before.guild.get_channel(int(self.logs[str(before.guild.id)]["channel"]))

        # Role checks
        if len(before.roles) > len(after.roles):
            for i in range(0, len(after.roles)):
                if before.roles[i] != after.roles[i]:
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0xbe4041)
                    self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                    self.embed.title = "Role removed"
                    self.embed.description = "<@&" + str(before.roles[i].id) + ">"

                    self.embed.set_footer(text="ID: " + str(after.id))
                    self.embed.timestamp = datetime.utcnow()

                    await loggingChannel.send(embed=self.embed)
                    break

        elif len(before.roles) < len(after.roles):
            if len(before.roles) == 1:
                self.embed = discord.Embed()
                self.embed.colour = discord.Colour(0x8899d4)
                self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                self.embed.title = "Role added"
                self.embed.description = "<@&" + str(after.roles[1].id) + ">"

                self.embed.set_footer(text="ID: " + str(after.id))
                self.embed.timestamp = datetime.utcnow()

                await loggingChannel.send(embed=self.embed)
                return

            for i in range(0, len(before.roles) + 1):
                if before.roles[i] != after.roles[i]:
                    self.embed = discord.Embed()
                    self.embed.colour = discord.Colour(0x8899d4)
                    self.embed.set_author(name=after.name + "#" + after.discriminator, icon_url=after.avatar_url)
                    self.embed.title = "Role added"
                    self.embed.description = "<@&" + str(after.roles[i].id) + ">"

                    self.embed.set_footer(text="ID: " + str(after.id))
                    self.embed.timestamp = datetime.utcnow()

                    await loggingChannel.send(embed=self.embed)
                    break

        # Nickname check
        elif before.nick != after.nick:
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

            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        """
        Sends a logging message containing
        the property of the user updated before and after
        """
        if self.logs["567169726250352640"]["channel"] is not None:

            loggingChannel = self.bot.get_guild(567169726250352640).get_channel(738536336016801793)

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

                await loggingChannel.send(embed=self.embed)

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
        loggingChannel = member.guild.get_channel(int(self.logs[str(member.guild.id)]["channel"]))

        if before.channel is None:
            self.embed = discord.Embed()
            self.embed.title = "Member joined voice channel"
            self.embed.description = "**" + member.display_name + "** joined #" + after.channel.name
            self.embed.colour = discord.Colour(0x43b581)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.set_footer(text="ID: " + str(member.id))
            await loggingChannel.send(embed=self.embed)

        elif after.channel is None:
            self.embed = discord.Embed()
            self.embed.title = "Member left voice channel"
            self.embed.description = "**" + member.display_name + "** left #" + before.channel.name
            self.embed.colour = discord.Colour(0xbe4041)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.set_footer(text="ID: " + str(member.id))
            await loggingChannel.send(embed=self.embed)

        elif before.channel.id != after.channel.id:
            self.embed = discord.Embed()
            self.embed.title = "Member changed voice channel"
            self.embed.description = "**Before: **#" + before.channel.name + "\n**+After: **#" + after.channel.name
            self.embed.colour = discord.Colour(0x8899d4)
            self.embed.set_author(name=member.name + "#" + member.discriminator, icon_url=member.avatar_url)
            self.embed.set_footer(text="ID: " + str(member.id))
            await loggingChannel.send(embed=self.embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """
        Sends a logging message containing
        the id, name, and join date of the member
        """
        return

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """
        Sends a logging message containing
        the id and name of the member
        """
        return

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """
        Sends a logging message containing
        the invite code, inviter name, inviter id, expiration time
        """

        return

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """
        Sends a logging message containing
        the invite code, inviter name, and expiration time
        """
        return
