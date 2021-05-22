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
        message = ""

        # Role checks
        added_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        final_roles = after.roles
        # If roles edited
        if len(added_roles) + len(removed_roles) > 0:
            role_list = []
            for role in after.roles:
                if role in Config.guilds[after.guild]["access_roles"]:
                    break
                if role in Config.guilds[after.guild]["opt_in_roles"]:
                    final_roles.remove(role)

        # WPI Specific checks
        if after.guild is not Config.main_guild:
            return

        class_roles = [
            Config.main_guild.get_role(787375833509658655),  # 2025
            Config.main_guild.get_role(664719508404961293),  # 2024
            Config.main_guild.get_role(567179738683015188),  # 2023
            Config.main_guild.get_role(578350297978634240),  # 2022
            Config.main_guild.get_role(578350427209203712),  # 2021
            Config.main_guild.get_role(692461531983511662),  # Mass Academy
            Config.main_guild.get_role(638748298152509461),  # WPI Staff
            Config.main_guild.get_role(599319106478669844),  # Graduate Student
            Config.main_guild.get_role(634223378773049365)   # Alumni
        ]

        final_roles = after.roles
        reasons = ""

        # Check if the member qualifies for WPI Verified role
        if after.id in Config.guilds[after.guild]["verifications"]["wpi"].values():
            if Config.guilds[after.guild]["verifications"]["wpi_role"] not in after.roles:
                if any(item in after.roles for item in class_roles):
                    final_roles.append(Config.guilds[Config.main_guild]["verifications"]["wpi_role"])
                    reasons += "Picked up class role, previously verified\n"
                    # await after.add_roles(
                    #     Config.guilds[Config.main_guild]["verifications"]["wpi_role"],
                    #     reason="Picked up class role, previously verified"
                    # )
            else:
                for role in after.roles:
                    if role in class_roles:
                        break
                else:
                    final_roles.remove(Config.guilds[Config.main_guild]["verifications"]["wpi_role"])
                    reasons += "Removed class role\n"
                    # await after.remove_roles(
                    #     Config.guilds[Config.main_guild]["verifications"]["wpi_role"],
                    #     reason="Removed class role"
                    # )
                    message += f"**The Verified WPI role has been removed because you no longer have a class role.** " \
                               f"Don't worry - you can get it back again by picking up a class role.\n"

        # Check if the member qualifies for Member role
        if after in Config.guilds[after.guild]["verifications"]["member"]:
            if Config.guilds[after.guild]["verifications"]["member"][after]["verified"]:
                if Config.guilds[after.guild]["verifications"]["member_role"] not in after.roles:
                    if any(item in after.roles for item in Config.guilds[after.guild]["access_roles"]):
                        final_roles.append(Config.guilds[after.guild]["verifications"]["member_role"])
                        reasons += "Picked up access role, previously earned member\n"
                        # await after.add_roles(
                        #     Config.guilds[after.guild]["verifications"]["member_role"],
                        #     reason="Picked up access role, previously earned member"
                        # )
                else:
                    for role in after.roles:
                        if role in Config.guilds[after.guild]["access_roles"]:
                            break
                    else:
                        print(f"User: {after}")
                        final_roles.remove(Config.guilds[after.guild]["verifications"]["member_role"])
                        reasons += "Removed access role\n"

        # Check if the member qualifies for Venting role
        if after.guild.get_role(725887796312801340) in after.roles:
            if Config.guilds[after.guild]["verifications"]["wpi_role"] not in final_roles:
                final_roles.remove(after.guild.get_role(725887796312801340))
                reasons += "Not WPI Verified"
                # await after.remove_roles(
                #     after.guild.get_role(725887796312801340),
                #     reason="Not WPI Verified"
                # )
                message += f"**The Venting role has been removed because you no longer have the Verified WPI role.** To " \
                           f"gain access to venting you will need to pick up the role again after regaining the " \
                           f"Verified WPI role.\n"

        if after.roles != final_roles:
            await after.edit(roles=final_roles, reason=reasons)

            if len(message) > 0:
                await after.send(message)

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
                await member.edit(roles=[Config.main_guild.get_role(812877476824088596)])
            else:
                await member.edit(roles=[Config.guilds[Config.main_guild]["nitro_role"], Config.main_guild.get_role(812877476824088596)], reason="Used lockout command")

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
