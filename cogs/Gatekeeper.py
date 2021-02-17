from discord.ext import commands


class Gatekeeper(commands.Cog):
    """
    Pre-emptive ban list
    """

    def __init__(self, bot):
        self.bot = bot
        self.Sql = bot.Sql

    @commands.listener()
    async def on_member_join(self, member):
        pass

    @commands.group()
    async def gkban(self, ctx):
        """
        Manages Gatekeeper bans

        You must be a Gatekeeper mod to use these commands. This is a *separate*
        check from the regular moderator role check.
        """
        pass

    @gkban.command(name="add")
    async def add_ban(self, ctx, target, reason="No reason provided"):
        """
        Adds a ban to Gatekeeper. All bans must be removed manually once added
        """
        pass

    @gkban.command(name="list")
    async def list_bans(self, ctx):
        """
        Lists Gatekeeper bans with their reason.
        """
        pass

    @commands.group()
    async def gkmod(self, ctx):
        """
        Manages Gatekeeper mods
        """
        pass

    @gkmod.command(name="add")
    async def add_mod(self, ctx, target: discord.Member):
        """
        Adds a mod to Gatekeeper
        """
        pass

    @gkmod.command(name="remove")
    async def remove_mod(self, ctx, target: discord.Member):
        """
        Removes a Gatekeeper mod
        """
        pass

