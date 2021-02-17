from discord.ext import commands
import discord

import ast

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
    async def eval(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            "bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "__import__": __import__,
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = await eval(f"{fn_name}()", env)
        await ctx.send(result)

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


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
