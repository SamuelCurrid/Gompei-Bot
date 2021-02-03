from cogs.Permissions import moderator_perms
from collections import namedtuple
from discord.ext import commands
from datetime import datetime
from config import Config

import discord
import typing


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="closeServer")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def close_server(self, ctx):
        """
        Prevents users from picking up access roles
        """
        if Config.guilds[ctx.guild]["closed"]:
            await ctx.send("The server is already closed")
        else:
            Config.set_guild_closed(ctx.guild, True)
            await ctx.send("Closed the server")

    @commands.command(pass_context=True, name="openServer")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def open_server(self, ctx):
        """
        Allows users to pick up access roles
        """
        if not Config.guilds[ctx.guild]["closed"]:
            await ctx.send("The server is already open")
        else:
            Config.set_guild_closed(ctx.guild, False)
            await ctx.send("Opened the server")

    @commands.command(pass_context=True, aliases=["addReactionRole", "rradd"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def add_reaction_role(self, ctx, message: discord.Message, emoji: typing.Union[discord.Emoji, str], role: discord.Role):
        """
        Adds a reaction role to a message with the given emoji
        Usage: .addReactionRole <message> <role> <emote>

        :param ctx: context object
        :param message: message to add the reaction role to
        :param emoji: emoji to react with
        :param role: role tied to the reaction
        """
        try:
            await message.add_reaction(emoji)
        except discord.NotFound:
            await ctx.send("Could not find emoji \"" + emoji + "\"")
            return

        if Config.guilds[message.guild]["reaction_roles"]:
            if emoji in Config.guilds[message.guild]["reaction_roles"][message]["emojis"]:
                await ctx.send("This emoji is already being used for a reaction role on this message")
                return

        Config.add_reaction_role(message, emoji, role)
        await ctx.send("Added reaction role")

    @commands.command(pass_context=True, aliases=["removeReactionRole", "rrdelete", "rremove"])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def remove_reaction_role(self, ctx, message: discord.Message, emoji: typing.Union[discord.Emoji, str]):
        """
        Removes a reaction role from a message
        Usage: .removeReactionRole <message> <emoji>

        :param ctx: context object
        :param message: message to remove from
        :param emoji: emoji to remove
        """
        if message not in Config.guilds[message.guild]["reaction_roles"]:
            await ctx.send("There are no reaction roles on this message")
            return

        if emoji not in Config.guilds[message.guild]["reaction_roles"][message]["emojis"]:
            await ctx.send("This emote is not attached to a reaction role on the message")
            return

        Config.remove_reaction_role(message, emoji)
        await message.remove_reaction(emoji, self.bot.user)
        await ctx.send("Removed reaction role")

    @commands.command(pass_context=True, name="makeExclusive")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def make_exclusive(self, ctx, message: discord.Message):
        """
        Makes it so a user can only pick up one of the roles in the reaction message

        :param ctx: Context object
        :param message: Message with reaction roles
        """
        Config.set_reaction_message_exclusivity(message, True)
        await ctx.send("Made reaction role exclusive")

    @commands.command(pass_context=True, name="makeInclusive")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def make_inclusive(self, ctx, message: discord.Message):
        """
        Makes it so a user can pick up and have as many of the roles on the reaction message as they'd like

        :param ctx: Context object
        :param message: Message with reaction roles
        """
        Config.set_reaction_message_exclusivity(message, False)
        await ctx.send("Made reaction role inclusive")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Checks for a react on a reaction role

        :param payload:
        """
        # If react is in DMs
        if payload.guild_id is None:
            return

        # If a bot
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)

        if message in Config.guilds[guild]["reaction_roles"]:
            # Fake ctx for EmojiConverter
            ctx = namedtuple('Context', 'bot guild', module=commands.context)
            ctx.bot = self.bot
            ctx.guild = guild

            if payload.emoji.is_custom_emoji():
                emoji = await commands.EmojiConverter().convert(ctx, str(payload.emoji.id))
            else:
                emoji = str(payload.emoji)

            if emoji in Config.guilds[guild]["reaction_roles"][message]["emojis"]:
                reaction_role = Config.guilds[guild]["reaction_roles"][message]["emojis"][emoji]
                roles = payload.member.roles

                switched = False
                if Config.guilds[guild]["reaction_roles"][message]["exclusive"]:
                    for role in Config.guilds[guild]["reaction_roles"][message]["emojis"].values():
                        if role in payload.member.roles:
                            roles.remove(role)
                            switched = True
                            break

                roles.append(reaction_role)

                if Config.guilds[guild]["closed"]:
                    if reaction_role not in Config.guilds[guild]["access_roles"]:
                        await payload.member.edit(roles=roles, reason="Reaction role")
                    elif switched:
                        await payload.member.edit(roles=roles, reason="Reaction role")
                    else:
                        logging = Config.guilds[guild]["logging"]["overwrite_channels"]["mod"]

                        if logging is None:
                            logging = Config.guilds[guild]["logging"]["channel"]

                        if logging is not None:
                            embed = discord.Embed(title="Server closed", color=0xbe4041)
                            embed.set_author(
                                name=payload.member.name + "#" + payload.member.discriminator,
                                icon_url=payload.member.avatar_url
                            )

                            embed.description = "<@" + str(payload.member.id) + \
                                                "> failed to pick up a role due to server closure.\n\nRole: " + \
                                                reaction_role.mention

                            embed.set_footer(text="ID: " + str(payload.member.id))
                            embed.timestamp = datetime.utcnow()

                            await logging.send(embed=embed)
                else:
                    await payload.member.edit(roles=roles, reason="Reaction role")
                await message.remove_reaction(payload.emoji, payload.member)
