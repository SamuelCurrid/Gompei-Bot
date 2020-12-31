from GompeiFunctions import load_json
from Permissions import administrator_perms
from discord.ext import commands

import os


class Automod(commands.Cog):
    """
    Automatic moderation handler
    """

    def __init__(self, bot):
        self.bot = bot
        self.automod_settings = load_json(os.path.join("config", "automod.json"))
        self.settings = load_json(os.path.join("config", "settings.json"))

    @commands.command(pass_context=True, aliases="am")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def automod(self, ctx, command):
        """
        Top level handler for automod

        :param ctx: Context object
        :param command: automod command you'd like to use
        """
        if command.lower() is "info":
            await self.send_info(ctx)

    async def send_info(self, ctx):
        response = ""
        for setting in self.automod_settings:
            response += setting.replace("_", " ").title() + ": "
            if self.automod_settings[setting] is None:
                response += "Disabled"


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Check for ghost pinging
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check for excessive pings, check for rate limit, check for excessive white space, check for blacklisted phrases/words
        return
