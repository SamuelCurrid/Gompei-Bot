import random

import discord
from discord.ext import commands


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

class Minesweeper(commands.Cog):
    """
    Spoiler Minesweeper
    """

    @commands.command(pass_context=True, name="minesweeper")
    async def new_minesweeper(self, ctx, x_str = "8", y_str = "8"):
        if not (x_str.isdecimal() and y_str.isdecimal()):
            await ctx.send(f"Either {x_str} or {y_str} is not a valid dimension for a minesweeper board. Please use the format `minesweeper x y`.")
            return

        x = int(x_str)
        y = int(y_str)
        if x < 2 or y < 2:
            await ctx.send(f"{x}x{y} is too small for a minesweeper board. The minimum dimensions are 2x2.")
            return

        bomb_count = max(2, (x * y // 10) + random.randrange(0, x + y))
        board = self.create_board(x, y)
        self.place_bombs(board, bomb_count)
        self.place_neighbors(board)

        embed = discord.Embed(title="Spoiler Minesweeper", color=discord.Color.red()).set_footer(text=f'Find all {bomb_count} bombs!')
        embed.add_field(name="Minefield", value="\n".join(["".join([f"||{cell}||" for cell in row]) for row in board]))

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
                        if x + c >= 0 and x + c < len(board) and y + r >= 0 and y + r < len(board) and board[y + r][x + c] == bomb:
                            ct += 1
                board[y][x] = numbers[ct]
