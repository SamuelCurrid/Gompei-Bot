from config.Permissions import dm_commands, moderator_perms
from GompeiFunctions import load_json, save_json
from dateutil.parser import parse
from discord.ext import commands
from datetime import datetime

import asyncio
import discord
import os


class Voting(commands.Cog):
    """
    Create votes and let users vote on them.
    Currently only has support for handling one voting poll in a server
    """
    def __init__(self, bot):
        self.bot = bot
        self.settings = load_json(os.path.join("config", "settings.json"))
        self.votes = None
        self.vote_open = False
        self.poll_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_voting()

    async def load_voting(self):

        self.votes = load_json(os.path.join("config", "votes.json"))

        # If the poll hasn't been created, nothing to load
        if self.votes["close"] is None:
            return
        else:
            closes = parse(self.votes["close"])
            # If the poll has been closed
            if datetime.now() > closes:
                return
            else:
                self.vote_open = True
                await self.load_poll_message()
                await self.poll_timer(closes)

    async def load_poll_message(self):
        guild = self.bot.get_guild(self.settings["guild_id"])
        channel = guild.get_channel(self.votes["channel_id"])
        self.poll_message = await channel.fetch_message(self.votes["message_id"])

    async def update_poll_message(self):
        self.votes["votes"] = sorted(self.votes["votes"], key=lambda i: len(i["voters"]), reverse=True)

        lastVotes = 0
        lastCount = 1
        count = 1
        leaderboard = ""
        for option in self.votes["votes"]:
            if len(option["voters"]) == lastVotes:
                leaderboard += "**" + str(lastCount) + ". **" + option["name"] + " - " + str(len(option["voters"])) + "\n"
                count += 1
            else:
                leaderboard += "**" + str(count) + ". **" + option["name"] + " - " + str(len(option["voters"])) + "\n"
                lastVotes = len(option["voters"])
                lastCount = count
                count += 1

        embed = discord.Embed(title=self.votes["title"], color=0x43b581)
        embed.description = leaderboard
        await self.poll_message.edit(embed=embed)

    async def poll_timer(self, close_date):
        self.vote_open = True
        await asyncio.sleep((close_date - datetime.now()).total_seconds())
        await self.close_poll(None)

    @commands.command(pass_context=True, aliases=["closePoll"])
    @commands.check(moderator_perms)
    async def close_poll(self, ctx):
        """
        Closes the poll
        Usage: .closePoll

        :param ctx: context object
        """
        lastVotes = 0
        lastCount = 1
        count = 1
        leaderboard = ""
        for option in self.votes["votes"]:
            if len(option["voters"]) == lastVotes:
                leaderboard += "**" + str(lastCount) + ". **" + option["name"] + " - " + str(
                    len(option["voters"])) + "\n"
                count += 1
            else:
                leaderboard += "**" + str(count) + ". **" + option["name"] + " - " + str(len(option["voters"])) + "\n"
                lastVotes = len(option["voters"])
                lastCount = count
                count += 1

        embed = discord.Embed(title=self.votes["title"], color=0x43b581)
        embed.description = ":star: " + self.votes["votes"][0]["name"] + " :star:\n" + leaderboard
        await self.poll_message.edit(embed=embed)

        self.vote_open = False
        self.votes["close"] = None
        self.votes["title"] = None
        self.votes["channel_id"] = None
        self.votes["message_id"] = None
        self.votes["votes"] = None

        save_json(os.path.join("config", "votes.json"), self.votes)
        if ctx is not None:
            await ctx.send("Closed poll")

        await self.poll_message.edit()

    @commands.command(pass_context=True, aliases=['createOpenVote'])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def create_open_vote(self, ctx, channel: discord.TextChannel, title, close_timestamp, *, message):
        """
        Creates an open poll that users can add options to vote for
        Usage: .createOpenVote <channel> <title> <closeTime> <message>

        :param ctx: context object
        :param channel: channel for the poll
        :param title: embed title for the poll
        :param close_timestamp: closing time for the poll
        :param message: message to accompany the poll
        """
        if str(ctx.guild.id) in self.votes:
            await ctx.send("A vote is already running for this server")
        else:
            closes = parse(close_timestamp)

            if closes is None:
                await ctx.send("Not a valid close time")
            elif (closes - datetime.now()).total_seconds() < 0:
                await ctx.send("Close time cannot be before current time")
            else:
                modifier = 4
                for char in ctx.message.content[:ctx.message.content.find(close_timestamp)]:
                    if char == "\"":
                        modifier += 1

                embed = discord.Embed(title=title, color=0x43b581)

                self.poll_message = await channel.send(message + "```.addOption <option> - Create an option to vote for and cast your vote for it\n.vote <option> - Cast a vote for an option in the poll\n.removeVote <option> - Removes a vote you casted for an option\n.sendPoll - sends the poll embed (does not update live)```", embed=embed)

                self.votes = {"type": "open", "close": close_timestamp, "title": title, "channel_id": channel.id, "message_id": self.poll_message.id, "votes": []}
                save_json(os.path.join("config", "votes.json"), self.votes)
                await self.poll_timer(closes)

    @commands.command(pass_context=True, aliases=['createDecisionVote'])
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def create_decision_vote(self, ctx, channel: discord.TextChannel, title, close_timestamp, *, message):
        if str(ctx.guild.id) in self.votes:
            await ctx.send("A vote is already running for this server")
        else:
            closes = parse(close_timestamp)

            if closes is None:
                await ctx.send("Not a valid close time")
            elif (closes - datetime.now()).total_seconds() < 0:
                await ctx.send("Close time cannot be before current time")
            else:
                modifier = 4
                for char in ctx.message.content[:ctx.message.content.find(close_timestamp)]:
                    if char == "\"":
                        modifier += 1

                def check_author(msg):
                    return msg.author.id == ctx.author.id

                self.votes = {"type": "decision", "close": close_timestamp, "title": title, "channel_id": channel.id, "message_id": None, "votes": []}

                query = await ctx.send("What options would you like to add to this decision poll? (Put each option on a new line)")

                response = await self.bot.wait_for('message', check=check_author)

                options = response.content.splitlines()
                for option in options:
                    self.votes["votes"].append({"name": option, "creator": None, "voters": []})

                embed = discord.Embed(title=title, color=0x43b581)

                if len(self.votes["votes"]) == 0:
                    await ctx.send("You need at least one option in your poll")
                    return

                self.poll_message = await channel.send(message + "```.vote <option> - Cast a vote for an option in the poll\n.removeVote <option> - Removes a vote you casted for an option\n.sendPoll - sends the poll embed (does not update live)```", embed=embed)
                self.votes["message_id"] = self.poll_message.id
                await self.update_poll_message()
                save_json(os.path.join("config", "votes.json"), self.votes)
                await self.poll_timer(closes)

    @commands.command(pass_context=True, aliases=["addOption"])
    @commands.check(dm_commands)
    async def add_option(self, ctx):
        """
        Adds an option to the poll
        Usage: .addOption <option>

        :param ctx: context object
        """
        if not self.vote_open:
            await ctx.send("There is no poll currently open")
            return

        if not self.votes["type"] == "open":
            await ctx.send("Cannot add options to this type of poll")
            return

        user_option = ctx.message.content[ctx.message.content.find(" ") + 1:]

        if len(user_option) > 88:
            await ctx.send("This option is too long")
            return

        if not user_option.isalnum():
            if "-" in user_option:
                modified_string = user_option.replace("-", "")
                if not modified_string.isalnum():
                    await ctx.send("Channel names have to be alphanumeric")
                    return
        if not all(c.isdigit() or c.islower() or c == "-" for c in user_option):
            await ctx.send("Channel names must be lowercase")
            return
        elif " " in user_option or "\n" in user_option:
            await ctx.send("Channel names cannot contain spaces (try using a \"-\" instead)")
            return
        else:

            # Check if the user has an option already or if the option already exists
            for option in self.votes["votes"]:
                if option["creator"] == ctx.author.id:
                    await ctx.send("You already added an option to this poll")
                    return
                if user_option in option["name"]:
                    await ctx.send("This option already exists")
                    return

            self.votes["votes"].append({"name": user_option, "creator": ctx.author.id, "voters": [ctx.author.id]})
            save_json(os.path.join("config", "votes.json"), self.votes)
            await self.update_poll_message()
            await ctx.send("Successfully added your option")

    @commands.command(pass_context=True)
    @commands.check(dm_commands)
    async def vote(self, ctx):
        """
        Votes for an option in the poll
        Usage: .vote <option>

        :param ctx: context object
        """
        if not self.vote_open:
            await ctx.send("There is no poll currently open")
            return

        user_option = ctx.message.content[ctx.message.content.find(" ") + 1:]

        if self.votes["type"] == "open":
            for option in self.votes["votes"]:
                if user_option == option["name"]:
                    if ctx.author.id in option["voters"]:
                        await ctx.send("You already voted for this option")
                        return

                    option["voters"].append(ctx.author.id)
                    save_json(os.path.join("config", "votes.json"), self.votes)
                    await self.update_poll_message()
                    await ctx.send("Successfully voted for " + user_option)
                    return
        elif self.votes["type"] == "decision":
            print("got here")
            for option in self.votes["votes"]:
                if user_option == option["name"]:
                    if ctx.author.id in option["voters"]:
                        await ctx.send("You already voted for this option")
                        return
                    else:
                        for other_option in self.votes["votes"]:
                            if user_option != other_option["name"]:
                                if ctx.author.id in other_option["voters"]:
                                    def check_author(message):
                                        return message.author.id == ctx.author.id

                                    query = await ctx.send("You already voted for an option (" + other_option["name"] + "). Would you like to switch your vote to " + option["name"] + "? (Y/N)")

                                    response = await self.bot.wait_for('message', check=check_author)

                                    if response.content.lower() == "y" or response.content.lower() == "yes":
                                        other_option["voters"].remove(ctx.author.id)
                                        option["voters"].append(ctx.author.id)
                                        save_json(os.path.join("config", "votes.json"), self.votes)
                                        await self.update_poll_message()
                                        await ctx.send("Successfully voted for " + user_option)
                                    else:
                                        await ctx.send("Kept your vote for " + other_option["name"])

                                    return

                        option["voters"].append(ctx.author.id)
                        save_json(os.path.join("config", "votes.json"), self.votes)
                        await self.update_poll_message()
                        await ctx.send("Successfully voted for " + user_option)

                        return

        if self.votes["type"] == "open":
            await ctx.send("This option doesn't exist. If you'd like to add it do it with `" + self.settings["prefix"] + "addOption <option>`")
        else:
            await ctx.send("This option doesn't exist.")

    @commands.command(pass_context=True, aliases=["removeVote"])
    @commands.check(dm_commands)
    async def remove_vote(self, ctx):
        """
        Removes your vote for an option in the poll
        Usage: .removeVote <option>

        :param ctx: context object
        """
        if not self.vote_open:
            await ctx.send("There is no poll currently open")
            return

        user_option = ctx.message.content[ctx.message.content.find(" ") + 1:]
        count = 0
        for option in self.votes["votes"]:
            if user_option == option["name"]:
                if ctx.author.id not in option["voters"]:
                    await ctx.send("You haven't voted for this option")
                    return

                option["voters"].remove(ctx.author.id)
                if len(option["voters"]) == 0 and self.votes["type"] == "open":
                    self.votes["votes"].pop(count)
                save_json(os.path.join("config", "votes.json"), self.votes)
                await self.update_poll_message()
                await ctx.send("Successfully removed vote for " + user_option)
                return
            count += 1

        await ctx.send("This option doesn't exist")

    @commands.command(pass_context=True, aliases=["removeOption"])
    @commands.check(moderator_perms)
    async def remove_option(self, ctx):
        """
        Removes an option from the poll entirely
        Usage: .removeOption <option>

        :param ctx: context object
        """
        user_option = ctx.message.content[ctx.message.content.find(" ") + 1:]
        count = 0

        for option in self.votes["votes"]:
            if user_option == option["name"]:
                self.votes["votes"].pop(count)
                save_json(os.path.join("config", "votes.json"), self.votes)
                await self.update_poll_message()
                await ctx.send("Successfully removed option " + user_option)
                return
            count += 1

    @commands.command(pass_context=True, aliases=["sendPoll"])
    @commands.check(dm_commands)
    async def send_poll(self, ctx):
        """
        Sends the poll
        Usage: .sendPoll

        :param ctx: context object
        """
        if not self.vote_open:
            await ctx.send("There is no poll currently open")
            return

        lastVotes = 0
        lastCount = 1
        count = 1
        leaderboard = ""
        for option in self.votes["votes"]:
            if len(option["voters"]) == lastVotes:
                leaderboard += "**" + str(lastCount) + ". **" + option["name"] + " - " + str(
                    len(option["voters"])) + "\n"
                count += 1
            else:
                leaderboard += "**" + str(count) + ". **" + option["name"] + " - " + str(len(option["voters"])) + "\n"
                lastVotes = len(option["voters"])
                lastCount = count
                count += 1

        embed = discord.Embed(title=self.votes["title"], color=0x43b581)
        embed.description = leaderboard
        await ctx.send("This poll does not update live", embed=embed)
