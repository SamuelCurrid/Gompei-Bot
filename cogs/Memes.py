from discord.ext import commands

import discord


class Memes(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 87585011070414848 and (";)" in message.content or "(;" in message.content):
            emoji = await message.guild.fetch_emoji(798282806102982696)
            if emoji is not None:
                await message.add_reaction(emoji)
