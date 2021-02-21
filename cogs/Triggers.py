from discord.ext import commands

greetings = ["hello", "hi", "greetings", "howdy", "salutations", "hey", "oi", "dear", "yo ", "morning", "afternoon",
             "evening", "sup", "G'day", "good day", "bonjour"]
gompei_references = ["gompei", "672453835863883787", "goat"]
love_references = ["gompeiHug", "love", "ily", "<3", "❤"]
hate_references = ["fuck you", "sucks", "fucker", "idiot", "shithead", "eat shit", "hate"]
violent_references = ["kill", "murder", "attack", "skin", "ambush", "stab"]


class Triggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if any(x in message.content.lower() for x in gompei_references):
                if any(x in message.content.lower() for x in love_references):
                    await message.add_reaction("❤")
                elif any(x in message.content.lower() for x in hate_references):
                    await message.add_reaction("😢")
                elif any(x in message.content.lower() for x in greetings):
                    await message.add_reaction("👋")
                elif any(x in message.content.lower() for x in violent_references):
                    await message.add_reaction("😨")


def setup(bot):
    bot.add_cog(Triggers(bot))
