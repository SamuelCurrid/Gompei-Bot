from cogs.Administration import Administration
from cogs.DirectMessages import DirectMessages
from GompeiFunctions import time_delta_string
from cogs.Permissions import moderator_perms
from discord.ext import commands
from datetime import timedelta
from datetime import datetime

import discord
import pickle
import typing
import os
import re


class Punishments:
    """
    Punishment object
    """
    # Punishment functions
    punishments = {
        "mute": Administration.mute,
        "jail": Administration.jail,
        # "delete": Administration.delete_message,
        "DM":  DirectMessages.echo_pm,
        "warn": Administration.warn
    }

    def __init__(self):
        self.punishments = []


class Automod(commands.Cog):
    """
    Automod tools
    """

    def __init__(self, bot):
        self.bot = bot
        self.settings = self.load_settings()
        self.attachment_rate = {}
        self.mention_rate = {}
        self.message_rate = {}

    def load_settings(self):
        """
        Loads the automod settings
        
        :return:
        """
        try:
            return pickle.load(open(os.path.join("config", "automod.p"), "rb"))
        except (OSError, IOError) as e:
            return {
                "ignore_mods": False,
                "bad_words": {
                    "enabled": False,
                    "overwrites": {},
                    "punishment": None,
                    "words": {}
                },
                "attachment_rate": {
                    "enabled": False,
                    "overwrites": {},
                    "punishment": None,
                    "attachments": 0,
                    "seconds": 0
                },
                "mention_rate": {
                    "enabled": False,
                    "overwrites": {},
                    "punishment": None,
                    "mentions": 0,
                    "seconds": 0
                },
                "message_rate": {
                    "enabled": False,
                    "overwrites": {},
                    "punishment": None,
                    "messages": 0,
                    "seconds": 0
                }
            }

    def save_settings(self, settings):
        """
        Saves the automod settings
        """
        pickle.dump(settings, open(os.path.join("config", "automod.p"), "wb+"))

    @commands.group(case_insensitive=True, aliases=["a"])
    @commands.check(moderator_perms)
    async def automod(self, ctx):
        """
        Top level command for automod

        :param ctx: Context object
        """
        if ctx.invoked_subcommand is None:
            await self.automod_help(ctx, None)

    @automod.command(name="info")
    async def automod_info(self, ctx, subcommand: typing.Optional[str]):
        """
        Sends current automod settings

        :param ctx: Context object
        """

        if subcommand is None:
            now = datetime.now()
            attach_time = time_delta_string(now, now + timedelta(seconds=self.settings["attachment_rate"]["seconds"]))
            mention_time = time_delta_string(now, now + timedelta(seconds=self.settings["mention_rate"]["seconds"]))
            message_time = time_delta_string(now, now + timedelta(seconds=self.settings["message_rate"]["seconds"]))

            embed = discord.Embed(
                title="Automod Settings",
                description=f"**__Attachment Rate__**\n"
                            f"Enabled: {self.settings['attachment_rate']['enabled']}\n"
                            f"Number: {self.settings['attachment_rate']['attachments']}\n"
                            f"Time: {attach_time}\n"
                            f"\n"
                            f"**__Bad Words__**\n"
                            f"Enabled: {self.settings['bad_words']['enabled']}\n"
                            f"\n"
                            f"**__Mention Rate__**\n"
                            f"Enabled: {self.settings['mention_rate']['enabled']}\n"
                            f"Number: {self.settings['mention_rate']['mentions']}\n"
                            f"Time: {mention_time}\n"
                            f"\n"
                            f"**__Message Rate__**\n"
                            f"Enabled: {self.settings['message_rate']['enabled']}\n"
                            f"Number: {self.settings['message_rate']['messages']}\n"
                            f"Time: {message_time}"
            )

            await ctx.send(embed=embed)
            return

        # TODO Implement subcommand info

    @automod.command(name="help")
    async def automod_help(self, ctx, subcommand: typing.Optional[str]):
        """
        Sends help information for automod

        Usage: .automod help

        :param ctx: Context object
        :param subcommand: Specific command to show help for
        """
        if subcommand is None:
            embed = discord.Embed(
                title="Automod Commands",
                description="```\n"
                            "attachmentRate - Attachment rate commands\n"
                            "info           - Displays current automod settings\n"
                            "badWords       - Bad words commands\n"
                            "help [command] - Displays help info\n"
                            "mentionRate    - Mention rate commands\n"
                            "messageRate    - Message rate commands\n"
                            "```"
            )
            await ctx.send(embed=embed)
            return

        # TODO Implement subcommand help

    @automod.group(name="badWords", case_insensitive=True)
    async def automod_bad_words(self, ctx):
        """
        Top level command for bad words settings

        Usage: .automod badWords ...

        :param ctx: Context object
        """
        await self.automod_help(ctx, "badWords")

    @automod_bad_words.command(name="add")
    async def automod_add_bad_word(self, ctx, *, word: str):
        """
        Adds a word to the bad word list

        :param ctx: Context object
        :param word: Word to add
        """
        if word.lower() in self.settings["bad_words"]["words"]:
            await ctx.send(
                f"{word} is already in the bad words list",
                allowed_mentions=discord.AllowedMentions.none()
            )
            return

        self.settings["bad_words"]["words"][word.lower()] = {}
        self.save_settings(self.settings)
        await ctx.send(
            f"Successfully added {word} to the bad words list",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @automod_bad_words.command(name="remove")
    async def automod_remove_bad_word(self, ctx, *, word: typing.Union[int, str]):
        """
        Removes a word from the bad word list

        :param ctx: Context object
        :param word: Word or index of word to remove
        """
        if word.lower() not in self.settings["bad_words"]["words"]:
            await ctx.send(
                f"Did not find {word} in bad words list",
                allowed_mentions=discord.AllowedMentions.none()
            )
            return

        del self.settings["bad_words"]["words"][word.lower()]
        self.save_settings(self.settings)
        await ctx.send(
            f"Successfully removed {word} from the bad words list"
        )

    @automod_bad_words.command(name="list")
    async def automod_list_bad_words(self, ctx):
        """
        Lists out the current bad words

        :param ctx: Context object
        """
        embed = discord.Embed(
            title="Automod Bad Words List",
            description=f"{', '.join([x for x in self.settings['bad_words']['words']])}"
        )
        await ctx.send(embed=embed)

    @automod_bad_words.command(name="enable")
    async def automod_bad_words_enable(self, ctx):
        """
        Enables automod for bad words

        :param ctx: Context object
        """
        if self.settings["bad_words"]["enabled"]:
            await ctx.send("Automod for bad words is already enabled")
            return

        self.settings["bad_words"]["enabled"] = True
        self.save_settings(self.settings)
        await ctx.send("Successfully enabled bad words")

    @automod_bad_words.command(name="disable")
    async def automod_bad_words_disable(self, ctx):
        """
        Disables automod for bad words

        :param ctx: Context object
        """
        if not self.settings["bad_words"]["enabled"]:
            await ctx.send("Automod for bad words is already disabled")
            return

        self.settings["bad_words"]["enabled"] = False
        self.save_settings(self.settings)
        await ctx.send("Successfully disabled bad words")


    @automod.group(name="attachmentRate", case_insensitive=True)
    async def automod_attachment_rate(self, ctx):
        """
        Top level command for attachment rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod_attachment_rate.command(name="setRate")
    async def automod_set_attachment_rate(self, ctx, *, rate: str):
        """
        Sets the rate limit for attachments

        :param ctx: Context object
        :param rate: Rate to set to
        """
        # TODO Implement
        pass

    @automod.group(name="mentionRate", case_insensitive=True)
    async def automod_mention_rate(self, ctx):
        """
        Top level command for mention rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod.group(name="messageRate", case_insensitive=True)
    async def automod_message_rate(self, ctx):
        """
        Top level command for message rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    """
    POST CARL REPLACEMENT
    - Whitespace abuse
    - Ghost ping abuse
    - Username checks
    - Nickname checks
    - Status checks
    - Div abuse
    - Crashers
    """

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Checks automod settings on message

        :param message: Message object
        """
        if message.author.bot:
            return

        if self.settings["attachment_rate"]["enabled"]:
            await self.attachment_rate_check(message)
        if self.settings["bad_words"]["enabled"]:
            await self.bad_word_check(message)
        if self.settings["mention_rate"]["enabled"]:
            await self.mention_rate_check(message)
        if self.settings["message_rate"]["enabled"]:
            await self.message_rate_check(message)

    async def attachment_rate_check(self, message):
        """
        Checks to see if the attachment rate was reached on message

        :param message: Message to check
        """
        # TODO Implement
        pass

    async def bad_word_check(self, message):
        """
        Checks to see if a bad word triggers for given message
        TODO Fuzzy matching not working as intended

        :param message: Message to check
        """
        msg = "".join(message.content.lower().split()).replace("-", "")

        for word in self.settings["bad_words"]["words"]:
            if re.match(word, msg):
                # TODO Punishment functions
                pass

    async def mention_rate_check(self, message):
        """
        Checks to see if mention rate was reached on a message

        :param message: Message to check
        """
        # TODO Implement
        pass

    async def message_rate_check(self, message):
        """
        Checks ot see if message rate was reached on a message

        :param message: Message ot check
        """
        # TODO Implement
        pass


def setup(bot):
    bot.add_cog(Automod(bot))
