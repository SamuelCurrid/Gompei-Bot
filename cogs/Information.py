from GompeiFunctions import time_delta_string
from cogs.Permissions import command_channels
from discord.ext import commands
from datetime import datetime

import discord
import typing


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = discord.Embed(color=0x8899d4)

    @commands.command(pass_context=True, aliases=["i"])
    @commands.check(command_channels)
    @commands.guild_only()
    async def info(self, ctx, *, target: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.Role, discord.Emoji, discord.PartialEmoji, discord.Member, discord.User, str]):
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
            discord.PartialEmoji: self.emoji_info,
            discord.Member: self.user_info,
            discord.User: self.user_info,
            str: self.keywords
        }

        self.embed = discord.Embed()

        if isinstance(target, str):
            await switcher[type(target)](ctx, target)
        else:
            await switcher[type(target)](target)

        await ctx.send(embed=self.embed)

    async def channel_info(self, channel: typing.Union[discord.TextChannel, discord.VoiceChannel]):
        """
        Dumps channel info into the embed

        :param channel: Channel to gather info for
        """
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
        self.embed.description += "\n**Created:** " + channel.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(channel.created_at, datetime.utcnow()) + " ago)" + "\n\n**__Overwrites__\n**"

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

        if len(self.embed.description) > 2048:
            self.embed.description = self.embed.description[0:2047]

        self.embed.set_footer(text=str(channel.id))
        self.embed.timestamp = datetime.utcnow()

    async def role_info(self, role: discord.Role):
        """
        Dumps role info into the embed

        :param role: Role to gather info for
        """
        self.embed.title = "Role Info"

        self.embed.description = "**Name:** " + role.name
        self.embed.description += "\n**Mention:** " + role.mention
        self.embed.description += "\n**Members:** " + str(len(role.members))
        self.embed.description += "\n**(R,G,B):** " + str(role.color.to_rgb())
        self.embed.description += "\n**Hoisted:** " + str(role.hoist)
        self.embed.description += "\n**Mentionable:** " + str(role.mentionable)
        self.embed.description += "\n**Position:** " + str(role.position)
        self.embed.description += "\n**Created:** " + role.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(role.created_at, datetime.utcnow()) + " ago)"

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

    async def user_info(self, user: [discord.Member, discord.User]):
        """
        Dumps user info into the embed

        :param user: User to gather info for
        """
        self.embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
        self.embed.description = "[Avatar](" + str(user.avatar_url) + ")"
        self.embed.description += "\n**Mention:** <@" + str(user.id) + ">"

        if isinstance(user, discord.Member):
            self.embed.title = "Member info"
            self.embed.description += "\n**Display Name:** " + user.display_name

            role_value = ""
            for role in user.roles[1:]:
                role_value = "<@&" + str(role.id) + "> " + role_value

            if role_value == "":
                role_value = "None"
            self.embed.add_field(name="Roles", value=role_value, inline=True)
            self.embed.add_field(name="Created at", value=user.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(user.created_at, datetime.utcnow()) + " ago)", inline=True)
            self.embed.add_field(name="Joined at", value=user.joined_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(user.joined_at, datetime.utcnow()) + " ago)", inline=True)
        else:
            self.embed.title = "User info"
            self.embed.add_field(name="Created at", value=user.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(user.created_at, datetime.utcnow()) + " ago)", inline=True)

        if len(self.embed.description) > 2048:
            self.embed.description = self.embed.description[0:2047]

        self.embed.set_footer(text=str(user.id))
        self.embed.timestamp = datetime.utcnow()

    async def emoji_info(self, emoji: typing.Union[discord.Emoji, discord.PartialEmoji]):
        """
        Dumps emoji info into an embed

        :param emoji: Emoji to gather info for
        """
        self.embed.title = "Emoji Info"
        self.embed.description = "**[Image](" + str(emoji.url) + ")**"
        self.embed.description += "\n**Name:** " + emoji.name
        if emoji.animated:
            self.embed.description += "\n**Format:** \<a:" + emoji.name + ":" + str(emoji.id) + ">"
        else:
            self.embed.description += "\n**Format:** \<:" + emoji.name + ":" + str(emoji.id) + ">"
        self.embed.description += "\n**Animated:** " + str(emoji.animated)
        if isinstance(emoji, discord.Emoji):
            self.embed.description += "\n**Available:** " + str(emoji.available)
            self.embed.description += "\n**Created at:** " + emoji.created_at.strftime("%y-%m-%d %H:%M:%S") + " UTC\n(" + time_delta_string(emoji.created_at, datetime.utcnow()) + " ago)"

        self.embed.set_footer(text=str(emoji.id))
        self.embed.timestamp = datetime.utcnow()

    async def guild_info(self, guild: discord.Guild):
        """
        Dumps guild info into an embed

        :param guild: Guild to gather info for
        """
        self.embed.title = guild.name
        self.embed.set_thumbnail(url=guild.icon_url)

        if guild.mfa_level == 1:
            self.embed.description = "**2FA:** Required"
        else:
            self.embed.description = "**2FA:** Not Required"

        self.embed.description += "\n**Default Notifications:** " + str(guild.default_notifications)[18:].replace("_", " ").title()
        if guild.description is not None:
            self.embed.description += "**Description:** " + guild.description

        self.embed.description += "\n**Explicit Content Filter:** " + str(guild.explicit_content_filter).replace("_", " ").title()
        self.embed.description += "\n**Owner:** " + "<@" + str(guild.owner_id) + ">"
        self.embed.description += "\n**Region:** " + str(guild.region).replace("-", " ").title()
        self.embed.description += "\n**Verification Level:** " + str(guild.verification_level).title()

        resource_values = "[Icon](" + str(guild.icon_url) + ")"
        if guild.banner is not None:
            resource_values += "\n[Banner](" + str(guild.banner_url) + ")"
        if guild.splash is not None:
            resource_values += "\n[Splash](" + str(guild.splash_url) + ")"
        if guild.discovery_splash is not None:
            resource_values += "\n[Discovery Splash](" + str(guild.discovery_splash_url) + ")"

        feature_values = ""
        for feature in guild.features:
            feature_values += feature.replace("_", " ").title() + "\n"
        if feature_values == "":
            feature_values = "None"

        if guild.premium_subscription_count >= 30:
            boosts = "Level 3\n" + str(guild.premium_subscription_count) + "/30 boosts"
        elif guild.premium_subscription_count >= 15:
            boosts = "Level 2\n" + str(guild.premium_subscription_count) + "/30 boosts"
        elif guild.premium_subscription_count >= 2:
            boosts = "Level 1\n" + str(guild.premium_subscription_count) + "/15 boosts"
        else:
            boosts = "Level 0\n" + str(guild.premium_subscription_count) + "/2 boosts"

        humans = 0
        bots = 0
        for member in guild.members:
            if member.bot:
                bots += 1
            else:
                humans += 1

        self.embed.add_field(name="Resources", value=resource_values, inline=True)
        self.embed.add_field(name="Features", value=feature_values, inline=True)
        self.embed.add_field(name="Boosts", value=boosts, inline=True)
        self.embed.add_field(name="Members", value="Total: " + str(guild.member_count) + "\nHumans: " + str(humans) + "\nBots: " + str(bots), inline=True)
        self.embed.add_field(name="Channels", value="Text Channels: " + str(len(guild.text_channels)) + "\nVoice Channels: " + str(len(guild.voice_channels)) + "\nCategories: " + str(len(guild.categories)), inline=True)
        self.embed.add_field(name="Roles", value=str(len(guild.roles)) + " roles", inline=True)

        self.embed.set_footer(text=str(guild.id))
        self.embed.timestamp = datetime.utcnow()

    async def guild_role_info(self, guild: discord.Guild):
        """
        Dumps role list into the embed

        :param guild: Guild to gather role info from
        """
        self.embed.title = guild.name + " Roles"
        self.embed.description = ""
        for role in guild.roles[1:]:
            self.embed.description = "\n" + role.mention + self.embed.description

        self.embed.set_footer(text=str(guild.id))
        self.embed.timestamp = datetime.utcnow()

    async def keywords(self, ctx, keyword: str):
        """
        Checks for command keywords

        :param ctx: Context object
        :param keyword: Keyword to check
        """
        keyword = keyword.lower()

        if keyword == "server" or keyword == ctx.guild.name.lower():
            await self.guild_info(ctx.guild)
        elif keyword == "roles" or keyword == "role" or keyword == "r":
            await self.guild_role_info(ctx.guild)
        elif len(keyword) == 18 or len(keyword) == 17:
            try:
                user_id = int(keyword)
                await self.user_info(await self.bot.fetch_user(user_id))
            except ValueError:
                self.embed.title = "Unrecognized keyword"
                self.embed.description = "Make sure you have the correct name/ID"
                self.embed.timestamp = datetime.utcnow()
            except discord.NotFound:
                self.embed.title = "User not found"
                self.embed.description = "Make sure you have the correct ID"
                self.embed.timestamp = datetime.utcnow()
            except discord.HTTPException:
                self.embed.title = "HTTP Error"
                self.embed.description = "Bot could not connect with the gateway"
                self.embed.timestamp = datetime.utcnow()
        else:
            self.embed.title = "Unrecognized keyword"
            self.embed.description = "Make sure you have the correct name/ID"
            self.embed.timestamp = datetime.utcnow()
