from GompeiFunctions import load_json, save_json
from Permissions import administrator_perms
from discord.ext import commands

import Config
import pytimeparse
import os


class Automod(commands.Cog):
    """
    Automatic moderation handler
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, case_insensitive=True, aliases=["am"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def automod(self, ctx):
        """
        Automod command group
        Usage: .automod <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid automod command")

    @automod.command(aliases=["i"])
    async def info(self, ctx):
        """
        Sends automod info

        :param ctx: Context object
        """
        response = ""

        await ctx.send(response)

    # Message rate commands
    @automod.group(pass_context=True, case_insensitive=True, aliases=["messageRate", "msgRate", "msgR"])
    async def message_rate(self, ctx):
        """
        Message rate command group
        Usage: .automod messageRate <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid message rate command")

    @message_rate.command(pass_context=True, name="disable")
    async def message_rate_disable(self, ctx):
        """
        Disables message rate checks
        Usage: .automod messageRate disable

        :param ctx: Context object
        """
        Config.automod_setting_disable("message_rate")
        await ctx.send("Disabled message rate limit")

    @message_rate.command(pass_context=True, name="enable")
    async def message_rate_enable(self, ctx):
        """
        Enables message rate checks
        Usage: .automod messageRate enable

        :param ctx: Context object
        """
        Config.automod_setting_enable("message_rate")
        await ctx.send("Enabled message rate limit")

    @message_rate.command(pass_context=True, name="set")
    async def message_rate_set_rate(self, ctx, rate_limit):
        """
        Sets the rate limit for messages
        Usage: .automod messageRate set <rateLimit>

        :param ctx: Context object
        :param rate_limit: Rate limit in format <number>/<time>
        """
        try:
            number = int(rate_limit[:rate_limit.find("/")])
        except ValueError:
            await ctx.send("Not a valid rate limit format. Format: `<number>/<time>`")
            return

        seconds = pytimeparse.parse(rate_limit[rate_limit.find("/") + 1:])

        if seconds is None:
            await ctx.send("Not a valid time")
            return

        Config.automod_set_message_rate_limit(number, seconds)
        await ctx.send("Updated message rate limit to " + str(number) + " messages per " + str(seconds) + " seconds")

    @message_rate.command(pass_context=True, name="setPunishment")
    async def message_rate_set_punishment(self, ctx, *, punishment: str):
        """
        Sets the punishment for breaking the message rate
        Usage: .automod messageRate punishment

        :param ctx: Context object
        :param punishment: Punishment for member
        """
        # IMPLEMENT
        return

    # Bad words commands
    @automod.group(pass_context=True, case_insensitive=True, aliases=["badWords", "badWord"])
    async def bad_words(self, ctx):
        """
        Bad words command group
        Usage: .automod badWords <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid bad words command")

    @bad_words.command(pass_context=True, name="disable")
    async def bad_words_disable(self, ctx):
        """
        Disables bad words checks
        Usage: .automod badWords enable

        :param ctx: context object
        """
        Config.automod_setting_disable("bad_words")
        await ctx.send("Disabled bad word filtering")

    @bad_words.command(pass_context=True, name="enable")
    async def bad_words_enable(self, ctx):
        """
        Enables bad words checks
        Usage: .automod badWords enable

        :param ctx: Context object
        """
        Config.automod_setting_enable("bad_words")
        await ctx.send("Enabled bad word filtering")

    # Mention spam commands
    @automod.group(pass_context=True, case_insensitive=True)
    async def mentions(self, ctx):
        """
        Mention spam command group
        Usage: .automod mentions <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid mention spam command")

    @mentions.command(pass_context=True, name="disable")
    async def mentions_disable(self, ctx):
        """
        Disables mention spam checks
        Usage: .automod mentions enable

        :param ctx: Context object
        """
        Config.automod_setting_disable("mention_spam")
        await ctx.send("Disabled mention spam checking")

    @mentions.command(pass_context=True, name="enable")
    async def mentions_enable(self, ctx):
        """
        Enables mention spam checks
        Usage: .automod mentions enable

        :param ctx: Context object
        """
        Config.automod_setting_enable("mention_spam")
        await ctx.send("Enabled mention spam checking")

    # Whitespace spam commands
    @automod.group(pass_context=True, case_insensitive=True)
    async def whitespace(self, ctx):
        """
        Whitespace spam command group
        Usage: .automod whitespace <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid whitespace spam command")

    @whitespace.command(pass_context=True, name="disable")
    async def whitespace_disable(self, ctx):
        """
        Disables whitespace spam checks
        Usage: .automod whitespace enable

        :param ctx: Context object
        """
        Config.automod_setting_disable("whitespace")
        await ctx.send("Disabled whitespace spam checking")

    @whitespace.command(pass_context=True, name="enable")
    async def whitespace_enable(self, ctx):
        """
        Enables whitespace spam checks
        Usage: .automod whitespace enable

        :param ctx: Context object
        """
        Config.automod_setting_enable("whitespace")
        await ctx.send("Enabled whitespace spam checking")

    # Ghost ping commands
    @automod.group(pass_context=True, case_insensitive=True, aliases=["ghostPing"])
    async def ghost_ping(self, ctx):
        """
        Ghost ping command group
        Usage: .automod ghostPing <subcommand>

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Not a valid ghost ping command")

    @automod.command(pass_context=True, name="disable")
    async def ghost_ping_disable(self, ctx):
        """
        Disables ghost ping checks
        Usage: .automod ghostPing disable

        :param ctx: Context object
        """
        Config.automod_setting_disable("ghost_ping")
        await ctx.send("Disabled ghost ping checking")

    @automod.command(pass_context=True, name="enable")
    async def ghost_ping_enable(self, ctx):
        """
        Disables ghost ping checks
        Usage: .automod ghostPing enable

        :param ctx: Context object
        """
        Config.automod_setting_enable("ghost_ping")
        await ctx.send("Enabled ghost ping checking")

    # Listeners
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Check for ghost pinging
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check for excessive pings, check for rate limit, check for excessive white space, check for blacklisted phrases/words
        return
