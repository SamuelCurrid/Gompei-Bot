from cogs.Administration import Administration
from cogs.DirectMessages import DirectMessages
from GompeiFunctions import time_delta_string
from discord.ext import commands

import typing


class Punishments:
    """
    Punishment object
    """
    # Punishment functions
    punishments = {
        "mute": Administration.mute,
        "jail": Administration.jail,
        "delete": Administration.delete_message,
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

    @commands.group()
    def automod(self, ctx):
        """
        Top level command for automod

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod.command(name="info")
    def automod_info(self, ctx):
        """
        Sends current automod settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod.command(name="help")
    def automod_help(self, ctx, *, subcommand: str):
        """
        Sends help information for automod

        :param ctx: Context object
        :param subcommand: Specific command to show help for
        """
        # TODO Implement
        pass

    @automod.group(name="badWords")
    def automod_bad_words(self, ctx):
        """
        Top level command for bad words settings

        :param ctx: Context object
        """
        # TODO Implement
        # Currently only using strict matching
        # Possible fuzzy implementation in the future
        pass

    @automod_bad_words.command(name="add")
    def automod_add_bad_word(self, ctx, *, word):
        """
        Adds a word to the bad word list

        :param ctx: Context object
        :param word: Word to add
        """
        # TODO Implement
        pass

    @automod_bad_words.command(name="remove")
    def automod_remove_bad_word(self, ctx, *, word: typing.Optional[int, str]):
        """
        Removes a word from the bad word list

        :param ctx: Context object
        :param word: Word or index of word to remove
        """
        # TODO Implement
        pass

    @automod_bad_words.command(name="list")
    def automod_list_bad_words(self, ctx):
        """
        Lists out the current bad words

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod.group(name="attachmentRate")
    def automod_attachment_rate(self, ctx):
        """
        Top level command for attachment rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod_attachment_rate.command(name="setRate")
    def automod_set_attachment_rate(self, ctx, *, rate: str):
        """
        Sets the rate limit for attachments

        :param ctx: Context object
        :param rate: Rate to set to
        """
        # TODO Implement
        pass

    @automod.group(name="mentionRate")
    def automod_mention_rate(self, ctx):
        """
        Top level command for mention rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    @automod.group(name="messageRate")
    def automod_message_rate(self, ctx):
        """
        Top level command for message rate settings

        :param ctx: Context object
        """
        # TODO Implement
        pass

    """
    POST CARL REPLACEMENT
    - Whitespace abuse
    - Div abuse
    - Crashers
    """


def setup(bot):
    bot.add_cog(Automod(bot))
