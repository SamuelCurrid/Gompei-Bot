from discord.ext import commands


class Highlights(commands.Cog):
    """
    Highlights cog to alert users when keywords of interest are said in a server
    """
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Highlights(bot))
