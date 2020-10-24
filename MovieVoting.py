from Permissions import command_channels, administrator_perms
from GompeiFunctions import load_json, save_json
from discord.ext import commands
import requests
import discord
import math
import os


class MovieVoting(commands.Cog):

    def __init__(self, bot, key):
        self.bot = bot
        self.key = key
        self.embed = discord.Embed(title="Movie Night Voting")
        self.cached_voting = {}
        self.movie_list = {}
        self.user_list = {}
        self.movie_list = load_json(os.path.join("config", "movie_list.json"))
        self.user_list = load_json(os.path.join("config", "user_list.json"))
        self.emojiList = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "➡️": 1, "⬅️": -1}

    @commands.command(pass_context=True, aliases=["addMovie"])
    @commands.check(command_channels)
    async def add_movie(self, ctx):
        """
        Add a movie to our list from an IMDB link
        """
        if len(ctx.message.content) > 10:
            author = str(ctx.message.author.id)
            if author in self.user_list:
                author_votes = len(self.user_list[author]["requests"])
            else:
                author_votes = 0
            if author_votes < 2:
                title = ctx.message.content
                title = title[10:len(title)]
                if title[0:5] == "https":
                    end_id = title.index("/?")
                    imdb_id = title[27:end_id]
                    req = "http://www.omdbapi.com/?apikey=" + self.key + "&i=" + imdb_id + "&type=movie"
                else:
                    req = "http://www.omdbapi.com/?apikey=" + self.key + "&t=" + title + "&type=movie"

                response = requests.get(req)
                movie_details = response.json()
                title = movie_details.get("Title")

                if response == 404:
                    await ctx.send("(404) Movie not found. Please try another.")
                else:
                    if movie_details.get("Response") == "False":
                        await ctx.send("Movie not found. Please try another.")
                    elif title in self.movie_list:
                        await ctx.send(title + " is already present in the list.")
                    else:
                        self.movie_list[title] = {}
                        self.movie_list[title]["year"] = movie_details.get("Year")
                        self.movie_list[title]["director"] = movie_details.get("Director")
                        self.movie_list[title]["summary"] = movie_details.get("Plot")
                        self.movie_list[title]["image"] = movie_details.get("Poster")
                        self.movie_list[title]["id"] = movie_details.get("imdbID")
                        self.movie_list[title]["request"] = author
                        self.movie_list[title]["votes"] = [author]
                        if author in self.user_list:
                            self.user_list[author]["requests"].append(title)
                            self.user_list[author]["votes"].append(title)
                        else:
                            self.user_list[author] = {}
                            self.user_list[author]["requests"] = [title]
                            self.user_list[author]["votes"] = [title]
                        await ctx.send(title + " has been added to the list. By suggesting it, you have already voted for it! You have " + str(2 - (author_votes+1)) + " suggestions remaining.")

                        last_page = math.ceil(len(self.movie_list) / 9)
                        for embed in self.cached_voting:
                            if self.cached_voting[embed]["page"] == last_page:
                                await self.update_movie_message(self.cached_voting[embed]["message"])
            else:
                await ctx.send("You can only suggest up to two movies.")
        else:
            ctx.send("Please include a movie title.")

        save_json(os.path.join("config", "movie_list.json"), self.movie_list)
        save_json(os.path.join("config", "user_list.json"), self.user_list)

    @commands.command(pass_context=True, aliases=["removeMovie"])
    @commands.check(administrator_perms)
    async def remove_movie(self, ctx):
        """
        Removes a movies (admin command)
        """
        title = ctx.message.content
        if len(title) > 12:
            title = title[13:len(title)]

            if title in self.movie_list:
                self.user_list[self.movie_list[title]["request"]]["requests"].remove(title)
                for user in self.user_list.keys():
                    self.user_list[user]["votes"].remove(title)
                del self.movie_list[title]
                await ctx.send("Successfully removed " + title + ". ")
            else:
                await ctx.send("Movie \"" + title + "\" not found. ")

            save_json(os.path.join("config", "movie_list.json"), self.movie_list)
            save_json(os.path.join("config", "user_list.json"), self.user_list)
        else:
            await ctx.send("Please include a movie title.")

    @commands.command(pass_context=True, aliases=["resetMovies"])
    @commands.check(command_channels)
    async def reset_movies(self, ctx):
        """
        Resets the movie voting data to empty
        """
        if ctx.message.author.guild_permissions.administrator:
            self.movie_list = {}
            self.user_list = {}

            save_json(os.path.join("config", "movie_list.json"), self.movie_list)
            save_json(os.path.join("config", "user_list.json"), self.user_list)
            await ctx.send("Movie voting data successfully cleared.")
        else:
            await ctx.send("Only administrators have permission to use this command.")

    @commands.command(pass_context=True, aliases=["removeVote"])
    @commands.check(command_channels)
    async def remove_vote(self, ctx):
        """
        Removes the calling user's vote from a given movie
        """
        if len(ctx.message.content) > 12:
            title = ctx.message.content
            title = title[12:len(title)]
            author = str(ctx.message.author.id)
            if title in self.movie_list:
                if author in self.movie_list[title]["votes"]:
                    self.movie_list[title]["votes"].remove(author)
                    self.user_list[author]["votes"].remove(title)
                    if len(self.movie_list[title]["votes"]) == 0:
                        self.user_list[self.movie_list[title]["request"]]["requests"].remove(title)
                        del self.movie_list[title]
                        await ctx.send("Vote for " + title + " removed. Since you were the only vote for this movie, it has been removed from the list.")
                        return
                    else:
                        await ctx.send("Vote for " + title + " removed.")
                        return
                else:
                    await ctx.send("You have not voted for this movie.")
                    return
            else:
                await ctx.send("Movie not found.")
                return
        else:
            ctx.send("Please include a movie title.")

        save_json(os.path.join("config", "movie_list.json"), self.movie_list)
        save_json(os.path.join("config", "user_list.json"), self.user_list)

    @commands.command(pass_context=True, aliases=["movieInfo"])
    @commands.check(command_channels)
    async def movie_info(self, ctx):
        """
        Sends an embed listing the details of a given movie
        """
        if len(ctx.message.content) > 11:
            title = ctx.message.content
            title = title[11:len(title)]

            if title in self.movie_list:
                d = "*dir. " + self.movie_list[title]["director"] + "*\n" + self.movie_list[title]["summary"]
                info = discord.Embed(title=title + " (" + self.movie_list[title]["year"] + ")", description=d)
                info.set_thumbnail(url=self.movie_list[title]["image"])
                await ctx.send(embed=info)
            else:
                await ctx.send("Movie not found.")
        else:
            ctx.send("Please include a movie title.")

    @commands.command(pass_context=True)
    @commands.check(command_channels)
    async def vote(self, ctx):
        title = ctx.message.content
        if len(title) > 5:
            title = title[6:len(title)]
            author = str(ctx.message.author.id)
            movies = list(self.movie_list.keys())

            for index in range(0, len(movies)):
                if title.lower() == movies[index].lower():
                    if author not in self.movie_list[movies[index]]["votes"]:
                        self.movie_list[title]["votes"].append(author)
                        if author not in self.user_list:
                            self.user_list[author] = {"requests": [], "votes": []}
                        self.user_list[author]["votes"].append(title)
                        await ctx.send("Successfully voted for " + str(title))
                        return
                    else:
                        await ctx.send("You've already voted for this movie")
                        return

            await ctx.send("Movie not recognized")
            return
        else:
            await ctx.send("Please include a movie title.")

    @commands.command(pass_context=True, aliases=["myVotes"])
    @commands.check(command_channels)
    async def my_votes(self, ctx):
        """
        Sends an embed listing all of the movies that the calling user has voted for
        """
        author = str(ctx.message.author.id)
        if author in self.user_list:
            h = ctx.message.author.display_name + "'s Votes:"
            d = ""
            count = 0
            for title in self.user_list[author]["votes"]:
                count += 1
                d = d + str(count) + ". " + title + "\n"
            embed = discord.Embed(title=h, description=d)
            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You have not voted for any movies yet!")

    @commands.command(pass_context=True, aliases=["movieList", "listMovies"])
    @commands.check(command_channels)
    async def list_movies(self, ctx):
        """
        Sends an embed listing the movies & reactions to vote for them
        """
        # Sort the movies in movieList
        self.movie_list = {k: v for k, v in sorted(self.movie_list.items(), key=lambda item: len(item[1]["votes"]), reverse=True)}

        # Create movieList
        description = ""
        count = 0

        for movie in self.movie_list:
            count += 1
            description += "**" + str(count) + ". " + movie + "** " + "*(" + self.movie_list[movie]["year"] + ")*" + " ([IMDB](https://www.imdb.com/title/" + self.movie_list[movie]["id"] + "))" + " - " + str(len(self.movie_list[movie]["votes"])) + "\n\n"
            if count == 9:
                break

        # Send message and add to cache for updating later
        self.embed.description = description
        last_page = math.ceil(len(self.movie_list) / 9)
        self.embed.title = "Movie Night Voting (1/" + str(last_page) + ")"
        message = await ctx.send(embed=self.embed)
        self.cached_voting[message.id] = {"page": 1, "message": message}

        emojis = list(self.emojiList.keys())

        # Add reactions for voting / embed modification
        for i in range(0, count):
            await message.add_reaction(emojis[i])

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Adds a vote for a movie based on the reaction or updates a movie list embed
        """
        # If the reaction was added to a voting embed
        if reaction.message.id in self.cached_voting:
            # If the reaction wasn't added by a bot
            if not user.bot:
                # If not a custom emoji
                if isinstance(reaction.emoji, str):
                    page = self.cached_voting[reaction.message.id]["page"]
                    length = len(self.movie_list)

                    # If attempting to switch pages
                    if reaction.emoji == "⬅️" or reaction.emoji == "➡️":
                        # Check if page is in bounds
                        if 0 < (page + self.emojiList[reaction.emoji]) <= math.ceil(length / 9):
                            # Update to new page
                            self.cached_voting[reaction.message.id]["page"] += self.emojiList[reaction.emoji]
                            await self.update_movie_message(self.cached_voting[reaction.message.id]["message"])

                    # If attempting to vote for a movie
                    elif reaction.emoji in self.emojiList.keys():
                        index = self.emojiList[reaction.emoji] - 1
                        page = self.cached_voting[reaction.message.id]["page"]
                        index += 9 * (page - 1)
                        titles = list(self.movie_list.keys())

                        # If user has not already voted for the movie
                        if str(user.id) not in self.movie_list[titles[index]]["votes"]:
                            self.movie_list[titles[index]]["votes"].append(str(user.id))
                            if str(user.id) not in self.user_list:
                                self.user_list[str(user.id)] = {"requests": [], "votes": [titles[index]]}
                            else:
                                self.user_list[str(user.id)]["votes"].append(titles[index])

                            # Figure out how many positions the movie changed by
                            differential = 0
                            while len(self.movie_list[titles[index]]["votes"]) < len(self.movie_list[titles[index - (differential + 1)]]["votes"]):
                                differential += 1

                            # If the movie changed positions in leaderboard
                            if differential > 0:
                                # Min page number of leaderboard to update
                                page = math.floor((index - differential) / 9)

                                for messageID in self.cached_voting:
                                    if self.cached_voting[messageID]["page"] >= page:
                                        await self.update_movie_message(self.cached_voting[messageID]["message"])
                            else:
                                await self.update_movie_message(reaction.message)

                        save_json(os.path.join("config", "movie_list.json"), self.movie_list)

                # Remove reaction
                if not isinstance(reaction.message.channel, discord.channel.DMChannel):
                    await reaction.remove(user)

    async def update_movie_message(self, message):
        """
        Updates a movie list embed in the message
        """

        # Sort the movies in movieList
        self.movie_list = {k: v for k, v in sorted(self.movie_list.items(), key=lambda item: len(item[1]["votes"]), reverse=True)}
        titles = list(self.movie_list.keys())

        # Create movieList
        description = ""
        page = self.cached_voting[message.id]["page"]
        last_page = math.ceil(len(self.movie_list) / 9)
        count = (page - 1) * 9
        self.embed.title = "Movie Night Voting (" + str(page) + "/" + str(last_page) + ")"

        # Set range of movies to display
        for index in range((page - 1) * 9, page * 9):
            count += 1
            if index > len(titles) - 1:
                break
            description += "**" + str(count) + ". " + titles[index] + "**" + " ([IMDB](https://www.imdb.com/title/" + self.movie_list[titles[index]]["id"] + "))" + " - " + str(len(self.movie_list[titles[index]]["votes"])) + "\n\n"

        # Edit message
        self.embed.description = description
        await message.edit(embed=self.embed)
