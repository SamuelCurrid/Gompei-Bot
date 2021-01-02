from cogs.Permissions import administrator_perms
from GompeiFunctions import parse_id
from discord.ext import commands
from config import Config

import datetime
import discord


class DirectMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Forwards DM messages to the DM channel

        :param message: message
        """
        if not message.author.bot:
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

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
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

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
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

    @commands.Cog.listener()
    async def on_message_delete(self, message):
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

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
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

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        """
        Sends an on typing event to DM channel if someone is typing in the bots DMs

        :param channel: channel that the user is typing in
        :param user: user that is typing
        :param when: when the user was typing
        """
        if isinstance(channel, discord.channel.DMChannel) and not user.bot and Config.dm_channel is not None:
            await Config.dm_channel.trigger_typing()

    @commands.command(pass_context=True, aliases=["dmChannel"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_dm_channel(self, ctx, channel):
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