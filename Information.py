from GompeiFunctions import time_delta_string
from Permissions import moderator_perms
from discord.ext import commands
from datetime import datetime

import discord
import typing


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = discord.Embed(color=0x8899d4)

    @commands.command(pass_context=True, aliases=["i"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def info(self, ctx, *targets: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.Role, discord.Emoji, discord.PartialEmoji, discord.Member, discord.User, str]):
        """
        Info command that gives information for various discord items
        Usage: .info <item>

        :param ctx: Context object
        :param target: Target to get info for
        """
        switcher = {
            discord.TextChannel: self.channel_info,
            discord.VoiceChannel: self.channel_info,
            discord.Role: self.role_info,
            discord.Emoji: self.emoji_info,
            discord.Member: self.user_info,
            discord.User: self.user_info,
            str: self.keywords
        }

        for target in targets:
            self.embed = discord.Embed()
            await switcher[type(target)](target)
            await ctx.send(embed=self.embed)

    async def channel_info(self, channel: typing.Union[discord.TextChannel, discord.VoiceChannel]):
        self.embed.description = "**Name:** " + channel.name

        # If a text channel
        if isinstance(channel, discord.TextChannel):
            self.embed.title = "Text Channel Info"
            self.embed.description += "\n**Mention:** " + channel.mention
            if channel.topic is not None:
                self.embed.description += "\n**Description:** " + channel.topic
        # If a voice channel
        else:
            self.embed.title = "Voice Channel Info"
            self.embed.description += "\n**Bitrate:** " + str(channel.bitrate)
            self.embed.description += "\n**User Limit:** " + str(channel.user_limit)
        if channel.category is not None:
            self.embed.description += "\n**Category:** " + str(channel.category.name)

        self.embed.description += "\n**Position:** " + str(channel.position)
        self.embed.description += "\n**Created:** " + time_delta_string(channel.created_at, datetime.utcnow()) + "\n\n**__Overwrites__\n**"
        for target in channel.overwrites:
            self.embed.description += target.mention + "\n"
            for permission in channel.overwrites[target]:
                if permission[1] is not None:
                    self.embed.description += "​ ​ ​ ​ ​​ ​ ​ ​ ​ ​ ​ ​" + permission[0].replace("_", " ").title()
                    if permission[1] is True:
                        self.embed.description += " :white_check_mark:\n"
                    else:
                        self.embed.description += " :x:\n"

        self.embed.set_footer(text=str(channel.id))
        self.embed.timestamp = datetime.utcnow()

    async def role_info(self, role: discord.Role):
        self.embed.title = "Role Info"

        self.embed.description = "**Name:** " + role.name
        self.embed.description += "\n**Mention:** " + role.mention
        self.embed.description += "\n**Color:** " + str(role.color.to_rgb())
        self.embed.description += "\n**Position:** " + str(role.position)
        self.embed.description += "\n**Created:** " + time_delta_string(role.created_at, datetime.utcnow())
        self.embed.description += "\n**Members:** " + str(len(role.members)) + "\n\n**__Permissions__\n**"
        for permission in role.permissions:
            if permission[1] is not None:
                self.embed.description += permission[0].replace("_", " ").title()
                if permission[1] is True:
                    self.embed.description += " :white_check_mark:\n"
                else:
                    self.embed.description += " :x:\n"

        self.embed.set_footer(text=str(role.id))
        self.embed.timestamp = datetime.utcnow()

    async def user_info(self, user: [discord.Member, discord.User]):
        self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
        self.embed.description = "[Avatar](" + str(user.avatar_url) + ")"
        self.embed.description += "\n**Mention:** <@" + str(user.id) + ">"

        user.avatar_url
        user.mention

        if isinstance(user, discord.Member):
            self.embed.title = "Member info"
            self.embed.description += "\n**Display Name:** " + user.display_name

            role_value = ""
            for role in user.roles[1:]:
                role_value = "<@&" + str(role.id) + "> " + role_value

            self.embed.add_field(name="Roles", value=role_value, inline=True)
            self.embed.add_field(name="Created at", value=user.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(user.created_at, datetime.utcnow()) + " ago)", inline=True)
            self.embed.add_field(name="Joined at", value=user.joined_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(user.joined_at, datetime.utcnow()) + " ago)", inline=True)
        else:
            self.embed.title = "User info"

        self.embed.set_footer(text=str(user.id))
        self.embed.timestamp = datetime.utcnow()

        # member.created_at

    # TODO
    async def emoji_info(self, emoji: discord.Emoji):
        self.embed.title = "Emoji Info"
        self.embed.description = "**Name:** " + emoji.name
        self.embed.description += "**"

    # TODO server info
    async def keywords(self, keyword: str):
        if keyword.lower() is "server":
            True
        else:
            self.embed.title = "Unrecognized keyword"
            self.embed.description = "Make sure you have the correct name/id"
            self.embed.set_footer(text=None)
            self.embed.timestamp = None
