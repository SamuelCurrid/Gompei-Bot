from cogs.Permissions import dm_commands, administrator_perms
from discord.ext import commands
from config import Config

import discord


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """
        Removes opt in channel roles if losing access role

        :param before: Member before
        :param after: Member after
        """
        # Role checks
        added_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        for role in added_roles:
            if role.id == 630589807084699653:
                await after.send("Welcome to the " + after.guild.name + "!\n\nIf you have any "
                                                                        "questions, feel free to shoot them in "
                                                                        "#help-me. Hopefully we, or someone else in "
                                                                        "the community, can answer them :smile:.")

        # If roles edited
        if len(added_roles) + len(removed_roles) > 0:
            role_list = []
            for role in after.roles:
                if role in Config.guilds[after.guild]["access_roles"]:
                    return
                if role not in Config.guilds[after.guild]["opt_in_roles"]:
                    role_list.append(role)

            await after.edit(roles=role_list)

    @commands.command(pass_context=True)
    @commands.check(dm_commands)
    async def lockout(self, ctx):
        """
        Removes user roles and stores them to be returned after
        Usage: .lockout

        :param ctx: context object
        """
        member = await Config.main_guild.fetch_member(ctx.message.author.id)

        # Get lockout info
        if member in Config.lockouts:
            await ctx.send("You've already locked yourself out")
        else:
            Config.add_lockout(member)

            # Remove members roles (check if nitro booster)
            if member.premium_since is None:
                await member.edit(roles=[])
            else:
                await member.edit(roles=[Config.guilds[Config.main_guild]["nitro_role"]], reason="Used lockout command")

            # DM User
            await member.send("Locked you out of the server. To get access back just type \".letmein\" here")

    @commands.command(pass_context=True, aliases=["letMeIn"])
    @commands.check(dm_commands)
    async def let_me_in(self, ctx):
        """
        Returns user roles from a lockout command
        Usage: .letMeIn

        :param ctx: context object
        """
        member = await Config.main_guild.fetch_member(ctx.message.author.id)

        if member is None:
            # Member is not in guild
            await ctx.send("You are not in the server!")
        else:
            if member not in Config.lockouts:
                await ctx.send("You haven't locked yourself out")
            else:
                await member.edit(roles=Config.lockouts[member], reason="Used letmein command")
                Config.remove_lockout(member)

                await member.send("Welcome back to the server :)")

    @commands.command(pass_context=True, aliases=["addAccessRole"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def add_access_role(self, ctx, *roles: discord.Role):
        """
        Adds roles to the list that give read access to the server
        Usage: .addAccessRole <role(s)>

        :param ctx: context object
        :param roles: role(s) to add
        """
        if len(roles) == 0:
            await ctx.send("You must include a role to add")
        else:
            Config.add_access_roles(roles)
            await ctx.send("Successfully added roles")

    @commands.command(pass_context=True, aliases=["removeAccessRole"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def remove_access_role(self, ctx, *roles: discord.Role):
        """
        Removes roles from the access list
        Usage: .removeAccessRoles <role(s)>

        :param ctx: context object
        :param roles: role(s) to remove
        """
        if len(roles) == 0:
            await ctx.send("You must include a role to remove")
        else:
            Config.remove_access_roles(roles)
            await ctx.send("Successfully removed roles")

    @commands.command(pass_context=True, aliases=["addOptInRole"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def add_opt_in_role(self, ctx, *roles: discord.Role):
        """
        Adds roles to the opt in list that will be removed if a user loses an access role

        :param ctx: context object
        :param roles: role(s) to add
        """
        if len(roles) == 0:
            await ctx.send("You must include a role to add")
        else:
            Config.add_opt_in_roles(roles)
            await ctx.send("Successfully added roles")

    @commands.command(pass_context=True, aliases=["removeOptInRole"])
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def remove_opt_in_role(self, ctx, *roles: discord.Role):
        """
        Removes roles from the opt in list
        Usage: .removeOptInRole <role(s)>

        :param ctx: context object
        :param roles: role(s) to remove
        """
        if len(roles) == 0:
            await ctx.send("You must include a role to remove")
        else:
            Config.remove_opt_in_roles(roles)
            await ctx.send("Successfully removed roles")

def setup(bot):
    bot.add_cog(Roles(bot))
