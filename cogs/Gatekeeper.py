from discord.ext import commands
from . import sql
import discord

def is_gk_mod():
    async def predicate(ctx):
        bot = ctx.bot
        ses = bot.Sql()
        mod = (
        ses.query(sql.GatekeeperMods).filter(sql.GatekeeperMods.user_id ==
                str(ctx.author.id)).first() 
        )
        if mod is not None:
            return True
        else:
            return False
    return commands.check(predicate)
class Gatekeeper(commands.Cog):
    """
    Pre-emptive ban list
    """

    def __init__(self, bot):
        self.bot = bot
        self.Sql = bot.Sql

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ses = self.bot.Sql()
        ban = (ses.query(sql.GatekeeperBans).filter(sql.GatekeeperBans.user_id
            == str(member.id)).first())
        if ban is not None:
            await (member.ban(reason=f"Found in Gatekeeper blacklist. Reason: {ban.reason}"))
            return
        else:
            return

    @commands.group()
    @is_gk_mod()
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
        ses = self.bot.Sql()
        ban = (ses.query(sql.GatekeeperBans).filter(sql.GatekeeperBans.user_id
            == str(target)).first())
        if ban is not None:
            await ctx.send("Already banned")
            return
        else:
            new_ban = (sql.GatekeeperBans(user_id=target, reason=reason,
                    moderator=str(ctx.author.id)))
            ses.add(new_ban)
            ses.commit()
            await ctx.send(f"Added to banlist. If they're in the server, ban them with this: <@{target}>")
            return

    @gkban.command(name="list")
    async def list_bans(self, ctx):
        """
        Lists Gatekeeper bans with their reason.
        """
        ses = self.bot.Sql()
        bans = (ses.query(sql.GatekeeperBans).all())

        banlist = "**Gatekeeper Bans**\n"

        for ban in bans:
            banlist += f"{ban.user_id} - {reason}\n"

        await ctx.send(banlist)

    @commands.group()
    @commands.is_owner()
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
        ses = self.bot.Sql()
        mod = (ses.query(sql.GatekeeperMods).filter(sql.GatekeeperMods.user_id ==
                str(ctx.author.id)).first()
            )
        if mod is not None:
            await ctx.send("That user is already a moderator")
            return
        else:
            mod = sql.GatekeeperMods(user_id=str(ctx.author.id))
            ses.add(mod)
            ses.commit()
            await ctx.send("Done")

    @gkmod.command(name="remove")
    async def remove_mod(self, ctx, target: discord.Member):
        """
        Removes a Gatekeeper mod
        """
        ses = self.bot.Sql()
        mod = (ses.query(sql.GatekeeperMods).filter(sql.GatekeeperMods.user_id
                == str(ctx.author.id)).first()
            )
        if mod is not None:
            ses.delete(mod)
            ses.commit()
            await ctx.send("Done")
            return
        else:
            await ctx.send("That user is not a moderator")
            return

