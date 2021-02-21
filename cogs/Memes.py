from discord.ext import commands


class Memes(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 87585011070414848 and (";)" in message.content or "(;" in message.content):
            emoji = await message.guild.fetch_emoji(802971310782152724)
            if emoji is not None:
                await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Memes(bot))
