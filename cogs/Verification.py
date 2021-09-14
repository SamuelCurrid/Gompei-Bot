from cogs.Permissions import administrator_perms, moderator_perms
from GompeiFunctions import time_delta_string
from discord.ext import tasks, commands
from datetime import timedelta
from datetime import datetime
from config import Config


import pytimeparse
import asyncio
import discord


class Verification(commands.Cog):
    """
    WPI Verification system
    """

    def __init__(self, bot):
        self.bot = bot
        self.verification_check.start()
        self.uptime_thread = None

    @tasks.loop(seconds=5.0)
    async def verification_check(self):
        if Config.guilds[Config.main_guild]["verifications"]["wpi_role"] is None:
            return

        wpi_role = Config.guilds[Config.main_guild]["verifications"]["wpi_role"]
        new_users = Config.update_wpi_verifications()
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

        for user_id in new_users:
            member = Config.main_guild.get_member(user_id)
            if member is None:
                continue
            elif any(item in member.roles for item in class_roles):
                await member.add_roles(wpi_role, reason="Completed verification")
                try:
                    await member.send("You are now verified in the WPI Discord Server!")
                except discord.Forbidden:
                    print(f"Couldn't send verification message to {member.display_name} due to having locked their DMs")
            else:
                try:
                    await member.send(
                        "You are now verified in the WPI Discord! One last step, in order to get the " + wpi_role.name +
                        " role you must pick up a class role"
                    )
                except discord.Forbidden:
                    print(f"Couldn't send verification message to {member.display_name} due to having locked their DMs")

    @verification_check.before_loop
    async def before_verification_check(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Starts the timer to check for verifications
        """
        while True:
            time = datetime.now().replace(hour=9, minute=0, second=0) - datetime.now()
            if time.total_seconds() <= 0:
                time = (datetime.now().replace(hour=9, minute=0, second=0)) + timedelta(days=1) - datetime.now()

            await asyncio.sleep(time.total_seconds())

            for guild in Config.guilds:
                await self.check_verifications(guild)

    @commands.command(pass_context=True, name="memberRole")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_member_verification_role(self, ctx, role: discord.Role):
        """
        Sets the verification role for members

        :param ctx: Context object
        :param role: Role to set to
        """
        Config.set_member_role(role)
        await ctx.send("Set verification role to " + role.name)

    @commands.command(pass_context=True, name="unverify")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def unverify(self, ctx, member: discord.Member):
        """
        Unverifies and resets a members verification

        :param ctx: Context object
        :param member: Member to unverify
        """
        if member in Config.guilds[member.guild]["verifications"]["member"]:
            Config.unverify_member(member)
            if Config.guilds[member.guild]["verifications"]["member_role"] in member.roles:
                await member.remove_roles(
                    Config.guilds[member.guild]["verifications"]["member_role"],
                    reason="Manual unverify"
                )
                await ctx.send(f"Unverified {member.display_name}")
            else:
                await ctx.send(f"Wiped {member.display_name} verification progress")
        else:
            await ctx.send("This member has not started the verification process")

    @commands.command(pass_context=True, name="disableVerification")
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def disable_verification(self, ctx, member: discord.Member):
        """
        Disables verification for a member

        :param ctx: Context object
        :param member:  Member to disable verification for
        """
        Config.disable_member_verification(member)
        await ctx.send(f"Disabled {member.display_name}'s ability to become verified")

    @commands.command(pass_context=True, name="memberMessages")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_message_requirement(self, ctx, number: int):
        """
        Sets the number of verification messages required to become a member

        :param ctx: Context object
        :param number: Number of messages
        """
        Config.set_member_message_req(ctx.guild, number)
        await ctx.send("Updated the required messages to become verified to " + str(number))

    @commands.command(pass_context=True, name="memberTime")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_time_requirement(self, ctx, *, time: str):
        """
        Sets the number of verification messages required to become a member

        :param ctx: Context object
        :param time: Time required to get verified
        """
        seconds = pytimeparse.parse(time)
        if seconds is None:
            await ctx.send("Not a valid time, try again")

        delta = timedelta(seconds=seconds)

        Config.set_member_time_req(ctx.guild, delta)
        await ctx.send("Updated the required time to become verified to " + time_delta_string(datetime.now(), datetime.now() + delta))

    @commands.command(pass_context=True, name="wpiRole")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_wpi_verification_role(self, ctx, role: discord.Role):
        """
        Sets the verification role for WPI members

        :param ctx: Context object
        :param role: Role to set to
        """
        Config.set_wpi_member_role(role)
        await ctx.send("Set WPI verification role to " + role.name)

    @commands.command(pass_context=True, name="forceVerifications")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def force_verifications(self, ctx):
        await self.check_verifications(ctx.guild)

    async def check_verifications(self, guild):
        for member in Config.guilds[guild]["verifications"]["member"]:
            # If verification disabled or already verified
            if Config.guilds[guild]["verifications"]["member"][member]["verified"] is None \
                    or Config.guilds[guild]["verifications"]["member"][member]["verified"]:
                continue

            # If they meet the message req
            message_requirement = Config.guilds[guild]["verifications"]["message_req"]
            time_requirement = Config.guilds[guild]["verifications"]["time_req"]
            if Config.guilds[guild]["verifications"]["member"][member]["message_count"] >= message_requirement:
                # If they meet the time req
                if datetime.now() - Config.guilds[guild]["verifications"]["member"][member]["datetime"] > time_requirement:
                    await member.add_roles(
                        Config.guilds[guild]["verifications"]["member_role"],
                        reason="Verified member"
                    )
                    Config.verify_member(member)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        """
        Changes perms based on whether a mod is online. Checks to see if a user needs to be given verification roles

        :param before: Member before
        :param after: Member after
        """
        # Check if in WPI Discord
        if before.guild is not Config.main_guild:
            return

        # If a moderator has been updated
        if before.top_role.id == 576464175430238208 or before.top_role.id == 742118136458772551:

            moderators = Config.main_guild.get_role(742118136458772551).members
            for moderator in moderators:
                # Check if a moderator is online on desktop
                if moderator.desktop_status is discord.Status.online:
                    # If a moderator is offline and perms are reduced, raise them
                    if Config.main_guild.default_role.permissions.attach_files is False:
                        perms = before.guild.default_role.permissions
                        perms.add_reactions = perms.embed_links = perms.attach_files = perms.stream = True
                        await before.guild.default_role.edit(permissions=perms, reason="Moderators are online")

                        logging = Config.mod_uptime_thread

                        if logging is not None:
                            if Config.mod_uptime_thread is None:
                                Config.set_mod_uptime_thread(
                                    await logging.create_thread(
                                        name="Moderator Uptime",
                                        auto_archive_duration=1440,
                                        type=discord.ChannelType.public_thread
                                    )
                                )

                            if Config.mod_uptime_thread.archived:
                                await Config.mod_uptime_thread.edit(
                                    auto_archive_duration=1440
                                )

                            embed = discord.Embed(title="Moderators Online", color=0x43b581)

                            embed.description = "Perms elevated for unverified users"

                            embed.set_footer(text="ID: " + str(after.guild.id))
                            embed.timestamp = discord.utils.utcnow()

                            await logging.send(embed=embed)

                    return

            # If moderators are offline and perms are elevated, reduce them
            if Config.main_guild.default_role.permissions.attach_files is True:
                perms = before.guild.default_role.permissions
                perms.add_reactions = perms.embed_links = perms.attach_files = perms.stream = False
                await before.guild.default_role.edit(permissions=perms, reason="Moderators are not online")

                logging = Config.mod_uptime_thread

                if logging is not None:
                    if Config.mod_uptime_thread is None:
                        Config.set_mod_uptime_thread(
                            await logging.create_thread(
                                name="Moderator Uptime",
                                auto_archive_duration=1440,
                                type=discord.ChannelType.public_thread
                            )
                        )

                    if Config.mod_uptime_thread.archived:
                        await Config.mod_uptime_thread.edit(
                            auto_archive_duration=1440
                        )

                if logging is not None:
                    embed = discord.Embed(title="Moderators Offline", color=0xbe4041)

                embed.description = "Perms reduced for unverified users"

                embed.set_footer(text="ID: " + str(after.guild.id))
                embed.timestamp = discord.utils.utcnow()

                await logging.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Checks to see if a user is on the verification list. If not, adds them.

        :param message: Message
        """
        if message.guild is None or message.author.bot:
            return

        if message.author not in Config.guilds[message.guild]["verifications"]["member"]:
            Config.add_member(message.author)
        elif not Config.guilds[message.guild]["verifications"]["member"][message.author]["verified"] and \
                Config.guilds[message.guild]["verifications"]["member"][message.author]["verified"] is not None:
            Config.add_message(message.author)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """
        Removes from message for unverified members on deletion.

        :param message: Message
        """
        if message.author in Config.guilds[message.guild]["verifications"]["member"]:
            if not Config.guilds[message.guild]["verifications"]["member"][message.author]["verified"] and \
                    Config.guilds[message.guild]["verifications"]["member"][message.author]["verified"] is not None:
                Config.remove_message(message.author)


def setup(bot):
    bot.add_cog(Verification(bot))
