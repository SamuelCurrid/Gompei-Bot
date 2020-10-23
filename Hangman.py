import random
import os
from typing import Dict, List

import discord
from discord.ext import commands
from Permissions import command_channels


hangman_embed = discord.Embed(title="Reaction Hangman", color=discord.Color.red()).set_footer(text='Tip: search "regional" in the reaction menu')


class HangmanGame:
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
            self.updateStatus()

    def updateStatus(self):
        self.errors = len([c for c in self.guesses if c not in self.word])
        if self.errors > 5:
            self.visible = self.word
        else:
            self.visible = ''.join('*' if c not in self.guesses else c for c in self.word)
    

class Hangman(commands.Cog):
    """
    Reaction Hangman Interface
    """
    games: Dict[str, HangmanGame]
    words: List[str]

    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.words = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_dict()
    
    async def load_dict(self):
        with open(os.path.join("config", "dictionary.txt"), "r") as dictionary:
            # fewer than 6 letters doesn't make for as fun of a game!
            self.words = [s.lower() for s in dictionary.read().splitlines() if len(s) >= 6]

    @commands.command(pass_context=True, name="hangman")
    @commands.check(command_channels)
    async def hangman(self, ctx: commands.Context):
        """
        Starts a game of hangman
        """
        hangman = HangmanGame(random.choice(self.words))
        msg = await ctx.send(embed=self.render_embed(hangman))
        self.games[msg.id] = hangman

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Adds a guess and updates game state
        """
        guild = self.bot.get_guild(payload.guild_id)
        if payload.message_id in self.games and guild is not None and len(payload.emoji.name) == 1:
            letter = chr(ord(payload.emoji.name) - 127365)
            if letter >= 'a' and letter <= 'z':
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                hangman = self.games[payload.message_id]
                hangman.guess(letter)
                if '*' not in hangman.visible:
                    del self.games[payload.message_id]
                await message.edit(embed=self.render_embed(hangman))
                await message.clear_reaction(payload.emoji)

    
    def render_embed(self, hangman: HangmanGame):
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
        embed.add_field(name="Word", value=' '.join("🟦" if c == '*' else chr(ord(c) + 127365) for c in hangman.visible))

        #padding
        embed.add_field(name="\u200b", value="\u200b")

        if len(hangman.guesses) > 0:
            embed.add_field(name="Guesses", value=' '.join(chr(ord(c) + 127365) for c in hangman.guesses) + "\n\n\n")

        if hangman.errors > 5:
            embed.add_field(name="Result", value="You lose!")
        elif '*' not in hangman.visible:
            embed.add_field(name="Result", value="You win!")

        return embed
