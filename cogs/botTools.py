from discord.ext import commands

import os


class BotTools(commands.Cog):
    """Allows the bot owner to manage functions of the bot including (un|re|)loading cogs

    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def bot(self, ctx):
        """Manages the bot. Owner only"""

    @bot.command(name="reload")
    async def reload_cog(self, ctx, arg):
        """
        Reloads a cog from the filesystem

        Uses dot-notation. You do not need to add 'cogs.' in front of the cog name, that is implied
        """
        try:
            self.bot.unload_extension(f"cogs.{str(arg)}")
            self.bot.load_extension(f"cogs.{str(arg)}")
        except Exception as e:
            await ctx.send(f"**ERROR**: {type(e).__name__} - {e}")
        else:
            await ctx.send("Success")

    @bot.command(name="load")
    async def load_cog(self, ctx, arg):
        """
        Loads a cog into the bot
        """
        print(f"Attempting to load {str(arg)}")
        try:
            self.bot.load_extension(f"cogs.{str(arg)}")
        except Exception as e:
            await ctx.send(f"**ERROR**: {type(e).__name__} - {e}")
        else:
            await ctx.send("Success")

    @bot.command(name="unload")
    async def unload_cog(self, ctx, arg: str):
        """
        Unloads a cog from the bot
        """
        try:
            self.bot.unload_extension(f"cogs.{arg}")
        except Exception as e:
            await ctx.send(f"**ERROR**: {type(e).__name__} - {e}")
        else:
            await ctx.send("Success")

    @bot.command(name="list")
    async def list_cogs(self, ctx):
        """
        Lists loaded cogs
        """
        loaded_cogs = "Loaded cogs:\n"
        for k in self.bot.extensions.keys():
            loaded_cogs += f"{k}\n"
        await ctx.send(loaded_cogs)

    @bot.command(name="update")
    async def update_bot(self, ctx):
        """
        Uses git to update the bot
        """
        import subprocess

        async with ctx.typing():
            proc = subprocess.run(
                "/usr/bin/git pull",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )

            if proc.returncode != 0:
                await ctx.send(f"**ERROR**: {str(proc.stderr.decode('UTF-8'))}")
            else:
                await ctx.send(proc.stdout.decode("UTF-8"))

    @bot.command()
    async def die(self, ctx):
        """Makes the bot shutdown gracefully"""

        await ctx.send("Shutting down...")

        # Disconnect all VCs
        for vc in self.bot.voice_clients:
            await vc.disconnect()

        # Logs out
        await self.bot.logout()

        os.exit(0)


def setup(bot):
    bot.add_cog(BotTools(bot))
