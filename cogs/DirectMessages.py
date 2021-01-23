from cogs.Permissions import administrator_perms, moderator_perms
from GompeiFunctions import parse_id
from discord.ext import commands
from datetime import datetime
from config import Config

import discord
import typing


class DirectMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await ctx.send(
                "Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" +
                str(message.id) + ">)"
            )
        elif len(attachments) > 0:
            message = await user.send(files=attachments)
            await ctx.send(
                "Message sent (<https://discordapp.com/channels/@me/" + str(message.channel.id) + "/" +
                str(message.id) + ">)"
            )
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
                await ctx.send(
                    "Message edited (<https://discordapp.com/channels/" + str(ctx.guild.id) + "/" + str(channel.id) +
                    "/" + str(message_id) + ">)"
                )

    @commands.command(pass_context=True, name="rolePM", aliases=["pmRole"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def role_pm(self, ctx, role: discord.Role, *, msg):
        """
        Sends a private message to all users with given role
        Usage: .pmRole <role> <message>

        :param ctx: Context object
        :param role: Role to
        :param msg: Message to send
        """
        # Read attachments and message
        attachments = []
        if len(ctx.message.attachments) > 0:
            for i in ctx.message.attachments:
                attachments.append(await i.to_file())

        members = role.members

        def check_author(message):
            return message.author.id == ctx.author.id

        # Send message to user via DM
        if len(msg) > 0:
            await ctx.send(
                "You are about to send this message to " +
                str(len(role.members)) + "users. Are you sure you want to do this? (Y/N)"
            )

            response = await self.bot.wait_for('message', check=check_author)

            if response.content.lower() == "y" or response.content.lower() == "yes":
                for member in members:
                    await member.send(msg, files=attachments)
                await ctx.send("Message(s) sent to " + str(len(role.members)) + " members")
            else:
                await ctx.send("Cancelled role PM")

        elif len(attachments) > 0:
            await ctx.send(
                "You are about to send this message to " +
                str(len(role.members)) + "users. Are you sure you want to do this? (Y/N)"
            )

            response = await self.bot.wait_for('message', check=check_author)

            if response.content.lower() == "y" or response.content.lower() == "yes":
                for member in members:
                    await member.send(files=attachments)
                await ctx.send("Message(s) sent to " + str(len(role.members)) + " members")
            else:
                await ctx.send("Cancelled role PM")
        else:
            await ctx.send("No content to send")

    @commands.command(pass_context=True, name="pmHistory", )
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def pm_history(self, ctx, user: typing.Union[discord.Member, discord.User, str]):
        # Fetch user from ID
        if isinstance(user, str) and (len(user) == 18 or len(user) == 17):
            try:
                user = int(user)
                user = await self.bot.fetch_user(user)
            except ValueError:
                await ctx.send("Did not find the user")
                return
            except discord.NotFound:
                await ctx.send("Did not find the user with that ID")
                return
            except discord.HTTPException:
                await ctx.send("Bot could not connect with gateway")
                return

        dm_channel = user.dm_channel
        if dm_channel is None:
            dm_channel = await user.create_dm()

        content = ""
        messages = await dm_channel.history(limit=None, oldest_first=True).flatten()
        digits = len(str(len(messages)))
        count = 1

        attachments = {}
        for message in messages:
            content += "`" + str(count).zfill(digits) + "` [<@" + str(message.author.id) + ">]: " + message.content + \
                       "\r"

            if len(message.attachments) > 0:
                attachments[count] = attachments

            count += 1

        if len(content) > 2048:
            chunks = []
            while len(content) > 0:
                chunk = content[: 2048]
                if len(attachments) > 1:
                    list(attachments.keys())[0]
                    m = chunk.count("\r")

                index = chunk.rfind("\r")
                chunks.append(chunk[: index])
                content = content[index + 1:]


            for i in range(0, len(chunks)):
                embed = discord.Embed(
                    title=user.display_name + " PM History (" + str(i + 1) + "/" + str(len(chunks)) + ")",
                    colour=discord.Colour(0xbe4041),
                    description=chunks[i]
                )

                embed.set_footer(text=str(user.id))
                embed.timestamp = datetime.utcnow()

                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=user.display_name + " PM History",
                colour=discord.Colour(0xbe4041),
                description=content
            )

            embed.set_footer(text=str(user.id))
            embed.timestamp = datetime.utcnow()

            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Forwards DM messages to the DM channel

        :param message: message
        """
        if Config.dm_channel is not None:
            if not message.author.bot:
                if isinstance(message.channel, discord.channel.DMChannel) and Config.dm_channel is not None:

                    message_embed = discord.Embed(description=message.content, timestamp=datetime.utcnow())
                    message_embed.set_author(
                        name="DM from " + message.author.name + "#" + message.author.discriminator,
                        icon_url=message.author.avatar_url
                    )
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

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """
        Forwards DM messages edited in DMs to a channel

        :param before: message before edit
        :param after: message after edit
        """
        if Config.dm_channel is not None:
            if isinstance(before.channel, discord.channel.DMChannel) and \
                    not before.author.bot and Config.dm_channel is not None:
                if before.content is after.content:
                    return

                message_embed = discord.Embed(timestamp=datetime.utcnow())
                message_embed.colour = discord.Colour(0x8899d4)
                message_embed.set_author(
                    name=after.author.name + "#" + before.author.discriminator,
                    icon_url=after.author.avatar_url
                )
                message_embed.title = "Message edited by " + after.author.name + "#" + str(after.author.discriminator)
                message_embed.description = "**Before:** " + before.content + "\n**+After:** " + after.content
                message_embed.set_footer(text="ID: " + str(before.author.id))
                message_embed.timestamp = datetime.utcnow()

                await Config.dm_channel.send(embed=message_embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        """
        Forwards DM uncached message edits to the DM channel

        :param payload: uncached message edit payload
        """
        if Config.dm_channel is not None:
            # If the message is not cached
            if payload.cached_message is None:
                guild = Config.main_guild
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

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Forwards DM message delete events to the DM channel

        :param message: Message that was deleted
        """
        if Config.dm_channel is not None:
            # If a DM message
            if isinstance(message.channel, discord.channel.DMChannel) \
                    and not message.author.bot \
                    and Config.dm_channel is not None:
                message_embed = discord.Embed(
                    title="Message deleted by " + message.author.name + "#" + str(message.author.discriminator),
                    colour=discord.Colour(0xbe4041),
                    description=message.content
                )
                message_embed.set_author(
                    name=message.author.name + "#" + message.author.discriminator,
                    icon_url=message.author.avatar_url
                )

                if len(message.attachments) > 0:  # Check for attachments
                    for attachment in message.attachments:
                        message_embed.add_field(name="Attachment", value=attachment.proxy_url)

                message_embed.set_footer(text="ID: " + str(message.author.id))
                message_embed.timestamp = datetime.utcnow()

                await Config.dm_channel.send(embed=message_embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Forwards DM uncached message delete events to the DM channel

        :param payload: Uncached deleted message payload
        """
        if Config.dm_channel is not None:
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

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        """
        Sends an on typing event to DM channel if someone is typing in the bots DMs

        :param channel: channel that the user is typing in
        :param user: user that is typing
        :param when: when the user was typing
        """
        if Config.dm_channel is not None:
            if isinstance(channel, discord.channel.DMChannel) and not user.bot and Config.dm_channel is not None:
                await Config.dm_channel.trigger_typing()

    @commands.command(pass_context=True, aliases=["dmChannel"])
    @commands.guild_only()
    @commands.is_owner()
    async def set_dm_channel(self, ctx, channel):
        """
        Sets the channel for DM events to be forwarded to
        Usage: .dmChannel <channel>

        :param ctx: context object
        :param channel: channel to set to
        """
        if ctx.guild != Config.main_guild:
            await ctx.send(
                "This bot isn't configured to work in this server! Read instructions on how to set it up here: "
                "<INSERT LINK>"
            )
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
