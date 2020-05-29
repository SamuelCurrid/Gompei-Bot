from discord.ext import commands
import os
import math
import json
import requests
import discord


class MovieVoting(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.embed = discord.Embed(title="Movie Night Voting")
		self.cachedVoting = {}
		self.movieList = {}
		self.userList = {}
		self.loadMovieList()
		self.loadUserList()
		self.emojiList = {"1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5, "6️⃣": 6, "7️⃣": 7, "8️⃣": 8, "9️⃣": 9, "➡️" : 1, "⬅️": -1}

	def loadMovieList(self):
		"""
		Loads the movie list from json file
		"""
		with open(os.path.join("config", "movieList.json"), "r+") as movieList:
			movies = movieList.read()
			self.movieList = json.loads(movies)

	def loadUserList(self):
		"""
		Loads the movie list from json file
		"""
		with open(os.path.join("config", "userList.json"), "r+") as userList:
			users = userList.read()
			self.userList = json.loads(users)

	async def updateMovieList(self):
		"""
		Updates the json file that contains the movie list
		"""
		with open(os.path.join("config", "movieList.json"), "r+") as movieList:
			movieList.truncate(0)
			movieList.seek(0)
			json.dump(self.movieList, movieList, indent=4)

	async def updateUserList(self):
		"""
		Updates the json file that contains the movie list
		"""
		with open(os.path.join("config", "userList.json"), "r+") as userList:
			userList.truncate(0)
			userList.seek(0)
			json.dump(self.userList, userList, indent=4)

	@commands.command(pass_context=True)
	async def addMovie(self, ctx):
		"""
		Add a movie to our list from an IMDB link
		"""
		author = str(ctx.message.author.id)
		if author in self.userList:
			authorVotes = len(self.userList[author]["requests"])
		else:
			authorVotes = 0
		if authorVotes < 2:
			title = ctx.message.content
			title = title[10:len(title)]
			req = "http://www.omdbapi.com/?apikey=2a4f4a86&t=" + title + "&type=movie"
			response = requests.get(req)
			movieDetails = response.json()
			title = movieDetails.get("Title")

			if response == 404:
				await ctx.send("Movie not found. Please try another.")
			else:
				if movieDetails.get("Response") == "False":
					await ctx.send("Movie not found. Please try another.")
				elif title in self.movieList:
					await ctx.send(title + " is already present in the list.")
				else:
					self.movieList[title] = {}
					self.movieList[title]["year"] = movieDetails.get("Year")
					self.movieList[title]["director"] = movieDetails.get("Director")
					self.movieList[title]["summary"] = movieDetails.get("Plot")
					self.movieList[title]["image"] = movieDetails.get("Poster")
					self.movieList[title]["id"] = movieDetails.get("imdbID")
					self.movieList[title]["request"] = author
					self.movieList[title]["votes"] = [author]
					if author in self.userList:
						self.userList[author]["requests"].append(title)
						self.userList[author]["votes"].append(title)
					else:
						self.userList[author] = {}
						self.userList[author]["requests"] = [title]
						self.userList[author]["votes"] = [title]
					await ctx.send(title + " has been added to the list. By suggesting it, you have already voted for it! You have " + str(2 - (authorVotes+1)) + " suggestions remaining.")
		else:
			await ctx.send("You can only suggest up to three movies.")

		await self.updateMovieList()
		await self.updateUserList()

	@commands.command(pass_context=True)
	async def removeMovie(self, ctx):
		"""
		Removes a movies (admin command)
		"""
		title = ctx.message.content
		title = title[13:len(title)]
		if ctx.message.author.guild_permissions.administrator:
			if len(title) > 12:
				if title in self.movieList:
					self.userList[self.movieList[title]["request"]]["requests"].remove(title)
					for user in self.userList.keys():
						self.userList[user]["votes"].remove(title)
					del self.movieList[title]
					await ctx.send("Successfully removed " + title + ". ")

				else:
					await ctx.send("Movie \"" + title + "\" not found. ")

			else:
				ctx.send("Please include a movie to remove.")
		else:
			ctx.send("You have to be an admin to use this command!")

		await self.updateMovieList()
		await self.updateUserList()

	@commands.command(pass_context=True)
	async def removeVote(self, ctx):
		"""
		Removes the calling user's vote from a given movie
		"""
		title = ctx.message.content
		title = title[12:len(title)]
		author = str(ctx.message.author.id)

		if title in self.movieList:
			if author in self.movieList[title]["votes"]:
				self.movieList[title]["votes"].remove(author)
				if len(self.movieList[title]["votes"]) == 0:
					self.userList[self.movieList[title]["request"]]["requests"].remove(title)
					if title in self.userList[author]["votes"]:
						self.userList[author]["votes"].remove(title)
					del self.movieList[title]
					await ctx.send("Vote for " + title + " removed. Since you were the only vote for this movie, it has been removed from the list.")
				else:
					await ctx.send("Vote for " + title + " removed.")
			else:
				await ctx.send("You have not voted for this movie.")
		else:
			await ctx.send("Movie not found.")

		await self.updateMovieList()
		await self.updateUserList()

	@commands.command(pass_context=True)
	async def movieInfo(self, ctx):
		"""
		Sends an embed listing the details of a given movie
		"""

		title = ctx.message.content
		title = title[11:len(title)]

		if title in self.movieList:
			d = "*dir. " + self.movieList[title]["director"] + "*\n" + self.movieList[title]["summary"]
			info = discord.Embed(title=title + " (" + self.movieList[title]["year"] + ")", description=d)
			info.set_thumbnail(url=self.movieList[title]["image"])
			await ctx.send(embed=info)
		else:
			await ctx.send("Movie not found.")

	@commands.command(pass_context=True)
	async def myVotes(self, ctx):
		"""
		Sends a embed that lists the movies that the calling user has voted for
		"""
		author = ctx.message.author.id

		if author in self.userList:
			title = ctx.message.author.nick + "'s Votes"
			votes = ""
			count = 0
			for title in self.userList[author]["votes"]:
				votes = votes + str(count + 1) + ". " + title
			embed = discord.Embed(title=title, description=votes)
			embed.set_thumbnail(url=ctx.message.author.avatar_url)
			await ctx.send(embed=embed)
		else:
			await ctx.send("You have not voted for anything yet")

	@commands.command(pass_context=True)
	async def listMovies(self, ctx):
		"""
		Sends an embed listing the movies & reactions to vote for them
		"""
		# Sort the movies in movieList
		self.movieList = {k: v for k, v in sorted(self.movieList.items(), key=lambda item: len(item[1]["votes"]), reverse=True)}

		# Create movieList
		description = ""
		count = 0

		for movie in self.movieList:
			count += 1
			description += "**" + str(count) + ". " + movie + "** " + "*(" + self.movieList[movie]["year"] + ")*" + " ([IMDB](https://www.imdb.com/title/" + self.movieList[movie]["id"] + "))" + " - " + str(len(self.movieList[movie]["votes"])) + "\n\n"
			if count == 9:
				break

		# Send message and add to cache for updating later
		self.embed.description = description
		message = await ctx.send(embed=self.embed)
		self.cachedVoting[message.id] = {"page": 1, "message": message}

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
		if reaction.message.id in self.cachedVoting:
			# If the reaction wasn't added by a bot
			if not user.bot:
				# If not a custom emoji
				if isinstance(reaction.emoji, str):
					page = self.cachedVoting[reaction.message.id]["page"]
					length = len(self.movieList)

					# If attempting to switch pages
					if reaction.emoji == "⬅️" or reaction.emoji == "➡️":
						#Check if page is in bounds
						if 0 < (page + self.emojiList[reaction.emoji]) <= math.ceil(length / 9):
							#Update to new page
							self.cachedVoting[reaction.message.id]["page"] += self.emojiList[reaction.emoji]
							await self.updateMovieMessage(self.cachedVoting[reaction.message.id]["message"])

					# If attempting to vote for a movie
					elif reaction.emoji in self.emojiList.keys():
						index = self.emojiList[reaction.emoji] - 1
						page = self.cachedVoting[reaction.message.id]["page"]
						index += 9 * (page - 1)
						titles = list(self.movieList.keys())

						# If user has not already voted for the movie
						if user.id not in self.movieList[titles[index]]["votes"]:
							self.movieList[titles[index]]["votes"].append(user.id)
							self.userList[user.id]["votes"].append(titles[index])

							# Figure out how many positions the movie changed by
							differential = 0
							while len(self.movieList[titles[index]]["votes"]) < len(self.movieList[titles[index - (differential + 1)]]["votes"]):
								differential += 1

							# If the movie changed positions in leaderboard
							if differential > 0:
								#Min page number of leaderboard to update
								page = math.floor((index - differential) / 9)

								for messageID in self.cachedVoting:
									if self.cachedVoting[messageID]["page"] >= page:
										await self.updateMovieMessage(self.cachedVoting[messageID]["message"])
							else:
								await self.updateMovieMessage(reaction.message)

						await self.updateMovieList()
				# Remove reaction

				if not isinstance(reaction.message.channel, discord.channel.DMChannel):
					await reaction.remove(user)


	async def updateMovieMessage(self, message):
		"""
		Updates a movie list embed in the message
		"""

		# Sort the movies in movieList
		self.movieList = {k: v for k, v in sorted(self.movieList.items(), key=lambda item: len(item[1]["votes"]), reverse=True)}
		titles = list(self.movieList.keys())

		# Create movieList
		description = ""
		page = self.cachedVoting[message.id]["page"]
		count = (page - 1) * 9

		# Set range of movies to display
		for index in range((page - 1) * 9, page * 9):
			count += 1
			if index > len(titles) - 1:
				break
			description += "**" + str(count) + ". " + titles[index] + "**" + " ([IMDB](https://www.imdb.com/title/" + self.movieList[titles[index]]["id"] + "))" + " - " + str(len(self.movieList[titles[index]]["votes"])) + "\n\n"


		# Edit message
		self.embed.description = description
		await message.edit(embed=self.embed)

