from GompeiFunctions import time_delta_string
from cogs.Permissions import command_channels
from discord.ext import commands
from datetime import datetime

import discord
import typing


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=["i"])
    @commands.check(command_channels)
    @commands.guild_only()
    async def info(self, ctx, *,
                   target: typing.Union[
                       discord.TextChannel,
                       discord.VoiceChannel,
                       discord.CategoryChannel,
                       discord.Role,
                       discord.Emoji,
                       discord.PartialEmoji,
                       discord.Member,
                       discord.User,
                       str
                   ]
                   ):
        """
        Info command that gives information for various discord items
        Usage: .info <item>

        :param ctx: Context object
        :param target: Target to get info for
        """
        switcher = {
            discord.TextChannel: self.channel_info,
            discord.VoiceChannel: self.channel_info,
            discord.CategoryChannel: self.channel_info,
            discord.Role: self.role_info,
            discord.Emoji: self.emoji_info,
            discord.PartialEmoji: self.emoji_info,
            discord.Member: self.user_info,
            discord.User: self.user_info,
            str: self.keywords
        }

        if isinstance(target, str):
            embed = await switcher[type(target)](ctx, target)
        else:
            embed = await switcher[type(target)](target)

        await ctx.send(embed=embed)

    async def channel_info(self, channel: typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]):
        """
        Dumps channel info into the embed

        :param channel: Channel to gather info for
        """
        f_description = "**Name:** " + channel.name

        # If a text channel
        if isinstance(channel, discord.TextChannel):
            title = "Text Channel Info"
            f_description += "\n**Mention:** " + channel.mention
            if channel.topic is not None:
                f_description += "\n**Description:** " + channel.topic
        # If a voice channel
        elif isinstance(channel, discord.VoiceChannel):
            title = "Voice Channel Info"
            f_description += "\n**Bitrate:** " + str(channel.bitrate) + \
                             "\n**User Limit:** " + str(channel.user_limit)
        else:
            title = "Category Info"
            if len(channel.text_channels) > 0:
                f_description += "\n**__Text Channels__**"
                for text_channel in channel.text_channels:
                    f_description += "\n" + text_channel.mention
            if len(channel.voice_channels) > 0:
                f_description += "\n**__Voice Channels__**"
                for voice_channel in channel.voice_channels:
                    f_description += "\n" + voice_channel.mention

        if channel.category is not None:
            f_description += "\n**Category:** " + str(channel.category.name)

        f_description += "\n**Position:** " + str(channel.position) + \
                         "\n**Created:** " + channel.created_at.strftime("%m-%d-%y %H:%M:%S") + \
                         " UTC\n(" + time_delta_string(channel.created_at, datetime.utcnow()) + " ago)" + \
                         "\n\n**__Overwrites__\n**"

        embed = discord.Embed(
            title=title,
            colour=discord.Colour(0x43b581),
            description=f_description
        )

        roles = []
        members = []
        for target in channel.overwrites:
            if isinstance(target, discord.Role):
                roles.append(target)
            else:
                members.append(target)

        targets = members + sorted(roles, key=lambda a: a.position, reverse=True)

        for target in targets:
            permissions = []
            values = []

            for permission in channel.overwrites[target]:
                if permission[1] is not None:
                    permissions.append(permission[0].replace("_", " ").title())
                    if permission[1] is True:
                        values.append("✔")
                    else:
                        values.append("✘")

            if len(permissions) > 0:
                max_length = len(max(permissions, key=len))

                f_description = "```"
                for i in range(0, len(permissions)):
                    f_description += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[i] + "\n"
                f_description += "```"

                embed.add_field(name=target.name, value=f_description, inline=True)

        if len(embed.description) > 2048:
            embed.description = embed.description[0:2047]

        embed.set_footer(text=str(channel.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def role_info(self, role: discord.Role):
        """
        Dumps role info into the embed

        :param role: Role to gather info for
        """
        embed = discord.Embed(
            title="Role Info",
            colour=role.colour,
            description=(
                    "**Name:** " + role.name +
                    "\n**Mention:** " + role.mention +
                    "\n**Members:** " + str(len(role.members)) +
                    "\n**(R,G,B):** " + str(role.color.to_rgb()) +
                    "\n**Hoisted:** " + str(role.hoist) +
                    "\n**Mentionable:** " + str(role.mentionable) +
                    "\n**Position:** " + str(role.position) +
                    "\n**Created:** " + role.created_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" +
                    "\n(" + time_delta_string(role.created_at, datetime.utcnow()) + " ago)"
            )
        )

        permissions = []
        values = []

        for permission in role.permissions:
            if permission[1] is not None:
                if permission[1] is True:
                    permissions.append(permission[0].replace("_", " ").title())
                    values.append("✔")

        if len(permissions) > 0:
            max_length = len(max(permissions, key=len))

            permission_values = "```"
            for i in range(0, len(permissions)):
                permission_values += permissions[i] + (" " * (max_length - len(permissions[i]))) + " " + values[
                    i] + "\n"
            permission_values += "```"

            embed.add_field(name="Permissions", value=permission_values, inline=True)

        if len(embed.description) > 2048:
            embed.description = embed.description[0:2047]

        embed.set_footer(text=str(role.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def user_info(self, user: [discord.Member, discord.User]):
        """
        Dumps user info into the embed

        :param user: User to gather info for
        """
        embed = discord.Embed(
            description=(
                    "[Avatar](" + str(user.avatar_url) + ")" +
                    "\n**Mention:** <@" + str(user.id) + ">"
            )
        )

        if isinstance(user, discord.Member):
            embed.title = "Member info"
            embed.description += "\n**Display Name:** " + user.display_name

            role_value = ""
            for role in user.roles[1:]:
                role_value = "<@&" + str(role.id) + "> " + role_value

            if role_value == "":
                role_value = "None"

            embed.colour = user.colour
            embed.add_field(name="Roles", value=role_value, inline=True)
            embed.add_field(
                name="Created at",
                value=(
                        user.created_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" +
                        "\n(" + time_delta_string(user.created_at, datetime.utcnow()) + " ago)"
                ),
                inline=True
            )
            embed.add_field(
                name="Joined at",
                value=(
                        user.joined_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" +
                        "\n(" + time_delta_string(user.joined_at, datetime.utcnow()) + " ago)"
                ),
                inline=True
            )
        else:
            embed.title = "User info"
            embed.colour = discord.Colour(0x43b581)
            embed.add_field(
                name="Created at",
                value=(
                        user.created_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" +
                        "\n(" + time_delta_string(user.created_at, datetime.utcnow()) + " ago)"
                ),
                inline=True
            )

        if len(embed.description) > 2048:
            embed.description = embed.description[0:2047]

        embed.set_author(name=user.name + "#" + user.discriminator, icon_url=user.avatar_url)
        embed.set_footer(text=str(user.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def emoji_info(self, emoji: typing.Union[discord.Emoji, discord.PartialEmoji]):
        """
        Dumps emoji info into an embed

        :param emoji: Emoji to gather info for
        """
        embed = discord.Embed(
            title="Emoji Info",
            colour=discord.Colour(0x43b581),
            description=(
                    "**[Image](" + str(emoji.url) + ")**" +
                    "\n**Name:** " + emoji.name
            )
        )

        if emoji.animated:
            embed.description += "\n**Format:** \<a:" + emoji.name + ":" + str(emoji.id) + ">"
        else:
            embed.description += "\n**Format:** \<:" + emoji.name + ":" + str(emoji.id) + ">"
        embed.description += "\n**Animated:** " + str(emoji.animated)
        if isinstance(emoji, discord.Emoji):
            embed.description += "\n**Available:** " + str(emoji.available)
            embed.description += "\n**Created at:** " + emoji.created_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" + \
                                 "\n(" + time_delta_string(emoji.created_at, datetime.utcnow()) + " ago)"

        embed.set_footer(text=str(emoji.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def guild_info(self, guild: discord.Guild):
        """
        Dumps guild info into an embed

        :param guild: Guild to gather info for
        """
        if guild.mfa_level == 1:
            description = "**2FA:** Required"
        else:
            description = "**2FA:** Not Required"

        embed = discord.Embed(
            title=guild.name,
            colour=discord.Colour(0x43b581),
            description=(
                    description +
                    "\n**Default Notifications: ** " + str(guild.default_notifications)[18:].replace("_", " ").title() +
                    "\n**Description: ** " + str(guild.description) +
                    "\n**Explicit Content Filter:** " + str(guild.explicit_content_filter).replace("_", " ").title() +
                    "\n**Owner:** " + "<@" + str(guild.owner_id) + ">" +
                    "\n**Region:** " + str(guild.region).replace("-", " ").title() +
                    "\n**Verification Level:** " + str(guild.verification_level).title()
            )
        )

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

        humans = bots = 0
        online = idle = dnd = offline = 0
        animated = static = 0
        playing = streaming = listening = watching = competing = 0

        for member in guild.members:
            # Counting humans vs. bots
            if member.bot:
                bots += 1
            else:
                humans += 1

            # Counting statuses
            if member.status is discord.Status.online:
                online += 1
            elif member.status is discord.Status.idle:
                idle += 1
            elif member.status is discord.Status.dnd:
                dnd += 1
            elif member.status is discord.Status.offline:
                offline += 1

            play = stream = listen = watch = compete = False

            # Counting activities
            for activity in member.activities:
                if isinstance(activity, discord.activity.Spotify):
                    if not listen:
                        listen = True
                        listening += 1
                elif isinstance(activity, discord.activity.Game):
                    if not play:
                        play = True
                        playing += 1
                elif isinstance(activity, discord.activity.Streaming):
                    if not stream:
                        stream = True
                        streaming += 1
                elif isinstance(activity, discord.activity.Activity):
                    if activity.type is discord.ActivityType.playing:
                        if not play:
                            play = True
                            playing += 1
                    elif activity.type is discord.ActivityType.streaming:
                        if not stream:
                            stream = True
                            streaming += 1
                    elif activity.type is discord.ActivityType.listening:
                        if not listen:
                            listen = True
                            listening += 1
                    elif activity.type is discord.ActivityType.watching:
                        if not watch:
                            watch = True
                            watching += 1
                    elif activity.type is discord.ActivityType.competing:
                        if not compete:
                            compete = True
                            competing += 1

        # Counting emojis
        for emoji in guild.emojis:
            if emoji.animated:
                animated += 1
            else:
                static += 1

        embed.add_field(name="Resources", value=resource_values, inline=True)
        embed.add_field(name="Features", value=feature_values, inline=True)
        embed.add_field(name="Boosts", value=boosts, inline=True)
        embed.add_field(
            name="Members",
            value=(
                    "Total: " + str(guild.member_count) +
                    "\nHumans: " + str(humans) +
                    "\nBots: " + str(bots)
            ),
            inline=True
        )
        embed.add_field(
            name="Statuses",
            value=(
                    ":green_circle: " + str(online) +
                    "\n:yellow_circle: " + str(idle) +
                    "\n:red_circle: " + str(dnd) +
                    "\n:white_circle: " + str(offline)
            ),
            inline=True
        )
        embed.add_field(
            name="Activities",
            value=(
                    "\nCompeting: " + str(competing) +
                    "\nListening: " + str(listening) +
                    "\nPlaying: " + str(playing) +
                    "\nStreaming: " + str(streaming) +
                    "\nWatching: " + str(watching)
            ),
            inline=True
        )
        embed.add_field(
            name="Channels",
            value=(
                    "Text Channels: " + str(len(guild.text_channels)) +
                    "\nVoice Channels: " + str(len(guild.voice_channels)) +
                    "\nCategories: " + str(len(guild.categories))
            ),
            inline=True
        )
        embed.add_field(
            name="Emojis",
            value=(
                    "Total: " + str(len(guild.emojis)) +
                    "\nAnimated: " + str(animated) + " / " + str(guild.emoji_limit) +
                    "\nStatic: " + str(static) + " / " + str(guild.emoji_limit)
            ),
            inline=True
        )
        embed.add_field(name="Roles", value=str(len(guild.roles)) + " roles", inline=True)
        embed.add_field(
            name="Created",
            value=(
                    guild.created_at.strftime("%m-%d-%y %H:%M:%S") + " UTC" +
                    "\n(" + time_delta_string(guild.created_at, datetime.utcnow()) + " ago)"
            ),
            inline=True
        )
        # Playing, Listening, Watching, Streaming ACTIVITIES

        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text=str(guild.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def guild_role_info(self, guild: discord.Guild):
        """
        Dumps role list into the embed

        :param guild: Guild to gather role info from
        """
        description = ""
        for role in guild.roles[1:]:
            description = "\n" + role.mention + description

        embed = discord.Embed(
            title=guild.name + " Roles",
            colour=discord.Colour(0x43b581),
            description=description
        )

        embed.set_footer(text=str(guild.id))
        embed.timestamp = datetime.utcnow()

        return embed

    async def keywords(self, ctx, keyword: str):
        """
        Checks for command keywords

        :param ctx: Context object
        :param keyword: Keyword to check
        """
        keyword = keyword.lower()

        if keyword == "server" or keyword == ctx.guild.name.lower():
            embed = await self.guild_info(ctx.guild)
        elif keyword == "roles" or keyword == "role" or keyword == "r":
            embed = await self.guild_role_info(ctx.guild)
        elif keyword == "everyone" or keyword == "e":
            embed = await self.role_info(ctx.guild.default_role)
        elif len(keyword) == 18 or len(keyword) == 17:
            try:
                user_id = int(keyword)
                embed = self.user_info(await self.bot.fetch_user(user_id))
            except ValueError:
                embed = discord.Embed(
                    title="Unrecognized keyword",
                    colour=discord.Colour(0xbe4041),
                    descrpition="Make sure you have the correct name/ID"
                )
            except discord.NotFound:
                embed = discord.Embed(
                    title="User not found",
                    colour=discord.Colour(0xbe4041),
                    descrpition="Make sure you have the correct ID"
                )
            except discord.HTTPException:
                embed = discord.Embed(
                    title="HTTP Error",
                    colour=discord.Colour(0xbe4041),
                    descrpition="Bot could not connect with the gateway"
                )
        else:
            embed = discord.Embed(
                title="Unrecognized keyword",
                colour=discord.Colour(0xbe4041),
                descrpition="Make sure you have the correct name/ID"
            )

        return embed
