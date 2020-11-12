from discord.ext import commands, flags


class Automod(commands.Cog):
    """
    Automatic moderation handler
    """

    def __init__(self, bot):
        self.bot = bot