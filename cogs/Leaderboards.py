from cogs.Permissions import command_channels, administrator_perms
from GompeiFunctions import load_json, save_json
from datetime import datetime
from discord.ext import commands

import dateutil.parser
import discord
import os


default_leaderboard = {
    "last_update": None, "quotes_channel": None,
    "message_leaderboard": {},
    "reaction_leaderboard": {},
    "emoji_leaderboard": {},
    "quote_leaderboard": {}
}
embeds = {
    "message_leaderboard": discord.Embed(title="Message leaderboard", colour=discord.Colour.red()),
    "reaction_leaderboard": discord.Embed(title="Reaction Usage Leaderboard", colour=discord.Colour.red()),
    "quote_leaderboard": discord.Embed(
        title="Quotes Leaderboard",
        description="Calculated from mentions",
        colour=discord.Colour.red()
    ),
    "emoji_leaderboard": discord.Embed(title="Emoji leaderboard", colour=discord.Colour.red())
}


class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leaderboards = {}
        self.cached_messages = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Loads leaderboard states
        """
        self.leaderboards = load_json(os.path.join("config", "leaderboards.json"))
        await self.update_guilds()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Creates default settings for new guilds
        """
        global default_leaderboard

        if str(guild.id) not in self.leaderboards:
            self.leaderboards[str(guild.id)] = default_leaderboard
            save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        emoji_leaderboard = self.leaderboards[str(guild.id)]["emoji_leaderboard"]

        add_emoji = [x for x in after if x not in before]

        for emoji in add_emoji:
            emoji_leaderboard[str(emoji.id)] == 0

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        Removes guilds from the settings
        """
        self.leaderboards.pop(str(guild.id))
        save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Updates leaderboards based on sent message content
        """
        # If message was sent in a guild
        if isinstance(message.channel, discord.TextChannel):
            guild = message.channel.guild
            leaderboard = self.leaderboards[str(guild.id)]

            if not message.author.bot:
                # Check message author
                if str(message.author.id) not in leaderboard["message_leaderboard"]:
                    leaderboard["message_leaderboard"][str(message.author.id)] = 1
                else:
                    leaderboard["message_leaderboard"][str(message.author.id)] += 1

                # Check for quotes
                if str(message.channel.id) == leaderboard["quotes_channel"]:
                    for user in message.mentions:
                        if str(user.id) not in leaderboard["quote_leaderboard"]:
                            leaderboard["quote_leaderboard"][str(user.id)] = 1
                        else:
                            leaderboard["quote_leaderboard"][str(user.id)] += 1

                # Check for emojis
                for emoji in message.guild.emojis:
                    emoji_name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                    for index in range(0, message.content.count(emoji_name)):
                        leaderboard["emoji_leaderboard"][str(emoji.id)] += 1

            leaderboard["lastUpdate"] = message.created_at.isoformat()
            save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        Updates leaderboards based ond deleted message content
        """
        if payload.guild_id is not None:
            guild = self.bot.get_guild(payload.guild_id)
            leaderboards = self.leaderboards[str(guild.id)]

            if payload.cached_message is not None:
                message = payload.cached_message

                if not message.author.bot:
                    leaderboards["message_leaderboard"][str(message.author.id)] -= 1

                    if str(message.channel.id) == leaderboards["quotes_channel"]:
                        for user in message.mentions:
                            leaderboards["quotes_channel"][str(user.id)] -= 1

                    for emoji in self.bot.emojis:
                        emoji_name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                        for index in range(0, message.content.count(emoji_name)):
                            leaderboards["emoji_leaderboard"][str(emoji.id)] -= 1

                leaderboards["lastUpdate"] = message.created_at.isoformat()
                save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Updates reactions leaderboard and checks for leaderboard page changes
        """
        guild = self.bot.get_guild(payload.guild_id)
        if guild is not None:
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await guild.fetch_member(payload.user_id)

            # Update cached leaderboards
            if not payload.member.bot:
                if payload.message_id in self.cached_messages:
                    if payload.emoji.name == "➡️":
                        await self.update_leaderboard_message(message, 1)
                        await message.remove_reaction("➡️", user)
                    elif payload.emoji.name == "⬅️":
                        await self.update_leaderboard_message(message, -1)
                        await message.remove_reaction("⬅️", user)

            # Update reaction leaderboards
            if not payload.member.bot:
                reactions = self.leaderboards[str(payload.guild_id)]["reaction_leaderboard"]

                if payload.emoji.id is not None:
                    for guildEmoji in guild.emojis:
                        if payload.emoji.id == guildEmoji.id:
                            if ("<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">") not in reactions:
                                reactions["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] = 1
                            else:
                                reactions["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] += 1

                            break
                else:
                    if payload.emoji.name not in reactions:
                        reactions[str(payload.emoji.name)] = 1
                    else:
                        reactions[str(payload.emoji.name)] += 1

                if str(payload.emoji.id) in self.leaderboards[str(payload.guild_id)]["emoji_leaderboard"]:
                    self.leaderboards[str(payload.guild_id)]["emoji_leaderboard"][str(payload.emoji.id)] += 1

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """
        Updates the reaction leaderboard
        """
        guild = self.bot.get_guild(payload.guild_id)
        if guild is not None:
            # Update reaction leaderboards
            reaction_leaderboard = self.leaderboards[str(payload.guild_id)]["reaction_leaderboard"]

            if payload.emoji.id is not None:
                for guildEmoji in guild.emojis:
                    if payload.emoji.id == guildEmoji.id:
                        reaction_leaderboard["<:" + str(payload.emoji.name) + ":" + str(payload.emoji.id) + ">"] -= 1
                        break

            else:
                reaction_leaderboard[str(payload.emoji.name)] -= 1

            if str(payload.emoji.id) in self.leaderboards[str(payload.guild_id)]["emoji_leaderboard"]:
                self.leaderboards[str(payload.guild_id)]["emoji_leaderboard"][str(payload.emoji.id)] -= 1

    @commands.command(pass_context=True, name="quotes")
    @commands.guild_only()
    async def quotes(self, ctx):
        """
        Sends the quotes leaderboard
        Usage: .quotes

        :param ctx: context object
        """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.channel.id == 567179438047887381:
            await ctx.channel.trigger_typing()
            await self.message_leaderboard(ctx, "quotes")

    @commands.command(pass_context=True, name="messages")
    @commands.check(command_channels)
    @commands.guild_only()
    async def messages(self, ctx):
        """
        Sends the messages leaderboard
        Usage: .messages

        :param ctx: context object
        """
        await ctx.channel.trigger_typing()
        await self.message_leaderboard(ctx, "messages")

    @commands.command(pass_context=True, name="reactions")
    @commands.check(command_channels)
    @commands.guild_only()
    async def reactions(self, ctx):
        """
        Sends the reactions leaderboard
        Usage: .reactions

        :param ctx: context object
        """
        await ctx.channel.trigger_typing()
        await self.message_leaderboard(ctx, "reactions")

    @commands.command(pass_context=True, name="emojis")
    @commands.check(command_channels)
    @commands.guild_only()
    async def emojis(self, ctx):
        """
        Sends the emoji leaderboard
        Usage: .emojis

        :param ctx: context object
        """
        await ctx.channel.trigger_typing()
        await self.message_leaderboard(ctx, "emojis")

    @commands.command(pass_context=True, name="set")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def set_quote_channel(self, ctx, channel: discord.TextChannel):
        """
        Sets the quote channel

        :param ctx: context object
        :param channel: channel to set
        """
        guild = ctx.message.guild

        if self.leaderboards[str(guild.id)]["quotes_channel"] != str(channel.id):
            self.leaderboards[str(guild.id)]["quotes_channel"] = str(channel.id)

            print("Updating guild " + str(guild.id) + " to use quotes channel " + str(channel.id))

            self.leaderboards[str(guild.id)]["quote_leaderboard"] = {}
            self.leaderboards[str(guild.id)]["last_update"] = None

            async for message in guild.get_channel(channel.id).history(limit=None):
                if not message.author.bot:
                    for user in message.mentions:
                        if str(user.id) not in self.leaderboards[str(guild.id)]["quote_leaderboard"]:
                            self.leaderboards[str(guild.id)]["quote_leaderboard"][str(user.id)] = 1
                        else:
                            self.leaderboards[str(guild.id)]["quote_leaderboard"][str(user.id)] += 1

            save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)
            print("Finished updating quotes channel")

    @commands.command(pass_context=True, name="resetLeaderboard")
    @commands.check(administrator_perms)
    @commands.guild_only()
    async def reset_leaderboard(self, ctx):
        """
        Resets all leaderboard information.
        Usage: .resetLeaderboard

        :param ctx: context object
        """
        guild = ctx.message.guild

        await ctx.send("Resetting leaderboards...")

        self.leaderboards[str(guild.id)]["last_update"] = None

        self.leaderboards[str(guild.id)]["message_leaderboard"] = {}
        self.leaderboards[str(guild.id)]["reaction_leaderboard"] = {}
        self.leaderboards[str(guild.id)]["quote_leaderboard"] = {}
        self.leaderboards[str(guild.id)]["emoji_leaderboard"] = {}

        for emoji in guild.emojis:
            self.leaderboards[str(guild.id)]["emoji_leaderboard"][str(emoji.id)] = 0

        save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)
        await self.update_leaderboards()
        await ctx.send("Successfully reset leaderboards")

    async def score_leaderboard(self, guild, leaderboard, leaderboardType):
        leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda a: a[1], reverse=True)}

        past_score = 0
        offset = 0
        position = 0
        user_values = ""

        for participant in leaderboard:
            score = leaderboard[participant]

            if score == past_score:
                offset += 1
            else:
                position += offset + 1
                offset = 0
                past_score = score

            if leaderboardType == "reaction_leaderboard":
                name = str(participant)
            elif leaderboardType == "emoji_leaderboard":
                for emoji in guild.emojis:
                    if int(participant) == emoji.id:
                        name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                        break
            else:
                name = "<@" + str(participant) + ">"

            user_values += "**" + str(position) + ". " + name + "** - " + str(score) + "\n\n\t"

        if user_values == "":
            user_values = "None"

        return user_values

    async def update_leaderboard_message(self, message, modifier):
        """
        Updates existing leaderboard message
        """
        global embeds
        guild = message.channel.guild

        leaderboard_embed = embeds[self.cached_messages[message.id]["type"]]
        leaderboard = self.leaderboards[str(guild.id)][self.cached_messages[message.id]["type"]]

        page = self.cached_messages[message.id]["page"]

        if len(leaderboard) / 10 + 1 >= page + modifier > 0:
            page += modifier
            scores = await self.score_leaderboard(guild, leaderboard, self.cached_messages[message.id]["type"])
            leaderboard_embed.clear_fields()
            leaderboard_embed.add_field(
                name="User",
                value="".join(scores.split("\t")[(page - 1) * 10:page * 10]),
                inline=True
            )
            await message.edit(embed=leaderboard_embed)

            self.cached_messages[message.id]["page"] += modifier

    async def update_guilds(self):
        """
        Updates guilds included in leaderboards.json
        """
        global default_leaderboard

        saved_guilds = []
        for guild_id in self.leaderboards:
            saved_guilds.append(int(guild_id))

        guilds = []
        for guild in self.bot.guilds:
            guilds.append(guild.id)

        add_guilds = [x for x in guilds if x not in saved_guilds]
        remove_guilds = [x for x in saved_guilds if x not in guilds]

        # Add new guilds
        for guild_id in add_guilds:
            self.leaderboards[str(guild_id)] = default_leaderboard

        # Remove disconnected guilds
        for guild_id in remove_guilds:
            self.leaderboards.pop(str(guild_id))

        save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)

    async def update_leaderboards(self):
        """
        Updates leaderboards from last run
        """
        for guild_id in self.leaderboards:
            board = self.leaderboards[guild_id]
            last_update = board["last_update"]

            if last_update is not None:
                last_update = dateutil.parser.parse(board["last_update"])

            guild = self.bot.get_guild(int(guild_id))

            for channel in guild.text_channels:
                # Catch exceptions for no permissions
                try:
                    async for message in channel.history(limit=None, after=last_update):
                        if not message.author.bot:

                            # Message leaderboard
                            if str(message.author.id) not in board["message_leaderboard"]:
                                board["message_leaderboard"][str(message.author.id)] = 1
                            else:
                                board["message_leaderboard"][str(message.author.id)] += 1

                            # Quote leaderboard
                            if str(message.channel.id) == board["quotes_channel"]:
                                for user in message.mentions:
                                    if str(user.id) not in board["quote_leaderboard"]:
                                        board["quote_leaderboard"][str(user.id)] = 1
                                    else:
                                        board["quote_leaderboard"][str(user.id)] += 1

                            # Reaction + Emoji leaderboard
                            for reaction in message.reactions:
                                if type(reaction.emoji) is not str:
                                    if type(reaction.emoji) is not discord.partial_emoji.PartialEmoji:
                                        for guild_emoji in self.bot.get_guild(int(guild_id)).emojis:
                                            if reaction.emoji.id == guild_emoji.id:
                                                name = "<:" + \
                                                       str(reaction.emoji.name) + ":" + str(reaction.emoji.id) + \
                                                       ">"
                                                if name not in board["reaction_leaderboard"]:
                                                    board["reaction_leaderboard"][
                                                        "<:" + str(reaction.emoji.name) + ":" +
                                                        str(reaction.emoji.id) + ">"] = reaction.count
                                                else:
                                                    board["reaction_leaderboard"][
                                                        "<:" + str(reaction.emoji.name) + ":" +
                                                        str(reaction.emoji.id) + ">"] += reaction.count

                                                break

                                    if str(reaction.emoji.id) in board["emoji_leaderboard"]:
                                        board["emoji_leaderboard"][str(reaction.emoji.id)] += reaction.count

                                else:
                                    if str(reaction.emoji) not in board["reaction_leaderboard"]:
                                        board["reaction_leaderboard"][str(reaction.emoji)] = reaction.count
                                    else:
                                        board["reaction_leaderboard"][str(reaction.emoji)] += reaction.count

                            # Emoji check
                            for emoji in guild.emojis:
                                emoji_name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                                for index in range(0, message.content.count(emoji_name)):
                                    if str(emoji.id) in board["emoji_leaderboard"]:
                                        board["emoji_leaderboard"][str(emoji.id)] += 1
                                    else:
                                        board["emoji_leaderboard"][str(emoji.id)] = 1

                except discord.Forbidden:
                    print("Do not have read message history permissions for: " + str(channel))

            board["lastUpdate"] = datetime.utcnow().isoformat()

        save_json(os.path.join("config", "leaderboards.json"), self.leaderboards)
        print("Leaderboards up to date")

    async def message_leaderboard(self, ctx, board_type):
        """
        Creates a new message leaderboard
        """
        global embeds
        guild = ctx.message.guild

        if board_type == "quotes":
            leaderboard_type = "quote_leaderboard"
            leaderboard = self.leaderboards[str(ctx.message.guild.id)]["quote_leaderboard"]
            leaderboard_embed = embeds[leaderboard_type]
        elif board_type == "reactions":
            leaderboard_type = "reaction_leaderboard"
            leaderboard = self.leaderboards[str(ctx.message.guild.id)]["reaction_leaderboard"]
            leaderboard_embed = embeds[leaderboard_type]
        elif board_type == "emojis":
            leaderboard_type = "emoji_leaderboard"
            leaderboard = self.leaderboards[str(ctx.message.guild.id)]["emoji_leaderboard"]
            leaderboard_embed = embeds[leaderboard_type]
        else:
            leaderboard_type = "message_leaderboard"
            leaderboard = self.leaderboards[str(ctx.message.guild.id)]["message_leaderboard"]
            leaderboard_embed = embeds[leaderboard_type]

        leaderboard_embed.clear_fields()

        leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda a: a[1], reverse=True)}

        past_score = 0
        offset = 0
        position = 0
        user_values = ""

        for participant in leaderboard:
            score = leaderboard[participant]

            if score == past_score:
                offset += 1
            else:
                position += offset + 1
                offset = 0
                past_score = score

            if leaderboard_type == "reaction_leaderboard":
                name = str(participant)
            elif leaderboard_type == "emoji_leaderboard":
                for emoji in guild.emojis:
                    if int(participant) == emoji.id:
                        name = "<:" + emoji.name + ":" + str(emoji.id) + ">"
                        break
            else:
                name = "<@" + str(participant) + ">"

            user_values += "**" + str(position) + ". " + name + "** - " + str(score) + "\n\n\t"

        if user_values == "":
            user_values = "None"

        leaderboard_embed.add_field(name="User", value="".join(user_values.split("\t")[0:10]), inline=True)

        message = await ctx.send(embed=leaderboard_embed)
        self.cached_messages[message.id] = {"type": leaderboard_type, "page": 1}
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")


def setup(bot):
    bot.add_cog(Leaderboards(bot))
