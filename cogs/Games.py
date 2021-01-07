from cogs.Permissions import command_channels, dm_commands
from discord.ext import commands
from typing import Dict, List

import discord
import random
import os


hangman_embed = discord.Embed(
    title="Reaction Hangman",
    color=discord.Color.red()
).set_footer(text='Tip: search "regional" in the reaction menu')

bomb = ":anger:"
numbers = [
    ":zero:",
    ":one:",
    ":two:",
    ":three:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:"
]


class HangmanGame:  # Credit: https://github.com/TheUnlocked
    """
    Reaction Hangman Game Instance
    """
    word: str
    visible: str
    errors: int
    guesses: List[str]

    def __init__(self, word):
        # print(word)
        self.word = word
        self.guesses = []
        self.visible = '*' * len(word)
        self.errors = 0

    def guess(self, letter):
        if letter not in self.guesses:
            self.guesses.append(letter)
            self.update_status()

    def update_status(self):
        self.errors = len([c for c in self.guesses if c not in self.word])
        if self.errors > 5:
            self.visible = self.word
        else:
            self.visible = ''.join('*' if c not in self.guesses else c for c in self.word)


class Games(commands.Cog):
    hangman_games: Dict[str, HangmanGame]
    hangman_words: List[str]

    def __init__(self, bot):
        self.bot = bot
        self.hangman_games = {}
        self.hangman_words = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_dict()

    # Hangman (Credit: https://github.com/TheUnlocked)

    async def load_dict(self):
        with open(os.path.join("config", "dictionary.txt"), "r") as dictionary:
            # fewer than 6 letters doesn't make for as fun of a game!
            self.hangman_words = [s.lower() for s in dictionary.read().splitlines() if len(s) >= 6]

    @commands.command(pass_context=True, name="hangman")
    @commands.check(command_channels)
    async def hangman(self, ctx):
        """
        Starts a game of hangman
        Usage: .hangman

        :param ctx: context object
        """
        hangman = HangmanGame(random.choice(self.hangman_words))
        msg = await ctx.send(embed=self.render_hangman_embed(hangman))
        self.hangman_games[msg.id] = hangman

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Adds a guess and updates game state
        """
        guild = self.bot.get_guild(payload.guild_id)
        if payload.message_id in self.hangman_games and guild is not None and len(payload.emoji.name) == 1:
            letter = chr(ord(payload.emoji.name) - 127365)
            if 'a' <= letter <= 'z':
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                hangman = self.hangman_games[payload.message_id]
                hangman.guess(letter)
                if '*' not in hangman.visible:
                    del self.hangman_games[payload.message_id]
                await message.edit(embed=self.render_hangman_embed(hangman))
                await message.clear_reaction(payload.emoji)

    def render_hangman_embed(self, hangman: HangmanGame):
        """
        Generates a new embed representing the state of the hangman game
        """
        global hangman_embed
        embed = hangman_embed.copy()

        head = '()' if hangman.errors > 0 else '  '
        torso = '||' if hangman.errors > 1 else '  '
        left_arm = '/' if hangman.errors > 2 else ' '
        right_arm = '\\' if hangman.errors > 3 else ' '
        left_leg = '/' if hangman.errors > 4 else ' '
        right_leg = '\\' if hangman.errors > 5 else ' '
        diagram = f"``` {head}\n{left_arm}{torso}{right_arm}\n {left_leg}{right_leg}```"

        embed.add_field(name="Diagram", value=diagram)
        embed.add_field(
            name="Word",
            value=' '.join("🟦" if c == '*' else chr(ord(c) + 127365) for c in hangman.visible)
        )

        # padding
        embed.add_field(name="\u200b", value="\u200b")

        if len(hangman.guesses) > 0:
            embed.add_field(name="Guesses", value=' '.join(chr(ord(c) + 127365) for c in hangman.guesses) + "\n\n\n")

        if hangman.errors > 5:
            embed.add_field(name="Result", value="You lose!")
        elif '*' not in hangman.visible:
            embed.add_field(name="Result", value="You win!")

        return embed

    # Minesweeper (Credit: https://github.com/TheUnlocked)

    @commands.command(pass_context=True, name="minesweeper")
    @commands.check(command_channels)
    @commands.guild_only()
    async def new_minesweeper(self, ctx, x_str="8", y_str="8"):
        """
        Creates a new spoiler minesweeper game
        Usage: .minesweeper (x) (y)

        :param ctx: context object
        :param x_str: (optional) x dimension
        :param y_str: (optional) y dimension
        """
        if not (x_str.isdecimal() and y_str.isdecimal()):
            await ctx.send(
                f"Either {x_str} or {y_str} is not a valid dimension for a minesweeper board. "
                f"Please use the format `minesweeper x y`."
            )
            return

        x = int(x_str)
        y = int(y_str)
        if x < 2 or y < 2:
            await ctx.send(f"{x}x{y} is too small for a minesweeper board. The minimum dimensions are 2x2.")
            return
        elif x > 10 or y > 10:
            await ctx.send(f"{x}x{y} is too large for a minesweeper board. The maximum dimensions are 10x10.")
            return

        bomb_count = min(x * y - 1, max(2, (x * y // 10) + random.randrange(0, x + y)))
        board = self.create_board(x, y)
        self.place_bombs(board, bomb_count)
        self.place_neighbors(board)

        if any(any(cell == numbers[0] for cell in row) for row in board):
            while True:
                y = random.choice(range(len(board)))
                x = random.choice(range(len(board[y])))
                if board[y][x] == numbers[0]:
                    board[y][x] = None
                    break

        embed = discord.Embed(
            title="Spoiler Minesweeper",
            color=discord.Color.red()
        ).set_footer(text=f"Find all {bomb_count} bombs!")
        embed.add_field(
            name="Minefield",
            value="\n".join(["".join([numbers[0] if cell is None else f"||{cell}||" for cell in row]) for row in board])
        )

        await ctx.send(embed=embed)

    def create_board(self, x, y):
        return [[None for _ in range(x)] for _ in range(y)]

    def place_bombs(self, board, num):
        while num > 0:
            y = random.choice(range(len(board)))
            x = random.choice(range(len(board[y])))
            if board[y][x] is not None:
                continue
            board[y][x] = bomb
            num -= 1

    def place_neighbors(self, board):
        for y in range(len(board)):
            for x in range(len(board[y])):
                if board[y][x] == bomb:
                    continue
                ct = 0
                for c in range(-1, 2):
                    for r in range(-1, 2):
                        if 0 <= x + c < len(board[y]) and 0 <= y + r < len(board) and board[y + r][x + c] == bomb:
                            ct += 1
                board[y][x] = numbers[ct]

    # Dice

    @commands.command(pass_context=True)
    @commands.check(dm_commands)
    async def roll(self, ctx, number):
        """
        Rolls a die for the number
        Usage: .roll <number>

        :param ctx: context object
        :param number: number of sides on the die
        """
        if "d" in number:
            sides = 0
            try:
                if number[:number.find("d")] != "":
                    dice = int(number[:number.find("d")])
                else:
                    dice = 1
                sides = int(number[number.find("d") + 1:])
            except ValueError:
                await ctx.send("Could not parse this roll")
                return

            if dice < 1 or sides < 1:
                await ctx.send("Not a valid number of dice/sides")
                return

            total = 0
            response = " ("
            for i in range(0, dice):
                roll_num = random.randint(1, sides)
                total += roll_num
                response += str(roll_num)
                if i == dice - 1:
                    break
                response += " + "

            response += " = " + str(total) + ")"

            if dice == 1:
                response = ""

            if ctx.author.nick is not None:
                response = ctx.author.nick.replace("@", "") + " rolled a " + str(total) + "!" + response
            else:
                response = ctx.author.name.replace("@", "") + " rolled a " + str(total) + "!" + response

            if len(response) > 500:
                await ctx.send(response[:response.find("(") - 1])
            else:
                await ctx.send(response)
        else:
            try:
                sides = int(number)
            except ValueError:
                await ctx.send("Could not parse this roll")
                return

            if sides < 1:
                await ctx.send("Not a valid number of sides")
                return

            if ctx.author.nick is not None:
                await ctx.send(ctx.author.nick.replace("@", "") + " rolled a " + str(random.randint(1, sides)) + "!")
            else:
                await ctx.send(ctx.author.name.replace("@", "") + " rolled a " + str(random.randint(1, sides)) + "!")

