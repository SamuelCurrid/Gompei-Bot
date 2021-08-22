from cogs.Permissions import moderator_perms
from datetime import datetime, timezone
from discord.ext import commands

import dateutil.parser as parser
import discord
import typing


def has_embed(self, ctx):
    return ctx.author in self.embeds


class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embeds = {}

    # Fix grouping for sub commands
    @commands.group(pass_context=True)
    @commands.check(moderator_perms)
    @commands.guild_only()
    async def embed(self, ctx):
        """
        Top level command for embed building.

        :param ctx: Context object
        """

    @embed.command(pass_context=True, name="create")
    async def embed_create(self, ctx):
        if ctx.author in self.embeds:
            await ctx.send(
                "You are already working on an embed! Use `.embed cancel` to cancel it or `.embed done` to finalize it"
            )
            return

        embed_message = await ctx.send(
            "__**Embed Builder**__\n"
            "**Attributes**: `author`, `colour`, `description`, `footer`, `image`, `thumbnail`, `timestamp`, `title`, "
            "`url`\n\n"
            "**Commands**\n"
            "```\n"
            ".embed <attribute> <value> - sets the attribute to a value\n"
            ".embed addField <title> <value> - Adds a field with given title and value\n"
            ".embed removeField <number> - Removes specified field (1-indexed)\n"
            ".embed remove <attribute> - Removes specified attribute\n"
            ".embed send <channel> - Finalizes the embed and sends it given channel\n"
            ".embed cancel - Scraps the embed being worked on\n"
            ".embed reset - Resets the embed to an empty one"
            ".embed done - Finishes building the embed\n"
            "```",
            embed=discord.Embed()
        )

        self.embeds[ctx.author] = embed_message

    # Attributes

    @embed.command(pass_context=True, name="author")
    async def embed_author(self, ctx, author: discord.Member):
        if ctx.author in self.embeds:
            embed = self.embeds[ctx.author].embeds[0]
            embed.set_author(name=author.display_name, icon_url=str(author.avatar.url))

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="colour", aliases=["color"])
    async def embed_colour(self, ctx, colour: discord.Colour):
        if ctx.author in self.embeds:
            embed = self.embeds[ctx.author].embeds[0]
            embed.colour = colour

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="description")
    async def embed_description(self, ctx, *, description: str):
        if ctx.author in self.embeds:
            if len(description) > 2048:
                await ctx.send("Description is too long! (Max 2048 characters)")
                return

            embed = self.embeds[ctx.author].embeds[0]
            embed.description = description

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="footer")
    async def embed_footer(self, ctx, *, footer: str):
        if ctx.author in self.embeds:
            if len(footer) > 2048:
                await ctx.send("Footer is too long! (Max 2048 characters)")
                return

            embed = self.embeds[ctx.author].embeds[0]
            embed.set_footer(text=footer)

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="image")
    async def embed_image(self, ctx, image: typing.Optional[str]):
        if ctx.author in self.embeds:
            if image:
                embed = self.embeds[ctx.author].embeds[0]
                embed.set_image(url=image)
            else:
                embed = self.embeds[ctx.author].embeds[0]
                if len(ctx.message.attachments) > 0:
                    image = ctx.message.attachments[0].url
                    embed.set_image(url=image)
                else:
                    await ctx.send("You need to send an image to add to the embed.")
                    return

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="thumbnail")
    async def embed_thumbnail(self, ctx, image: typing.Optional[str]):
        if ctx.author in self.embeds:
            if image:
                embed = self.embeds[ctx.author].embeds[0]
                embed.set_thumbnail(url=image)
            else:
                embed = self.embeds[ctx.author].embeds[0]
                if len(ctx.message.attachments) > 0:
                    image = ctx.message.attachments[0].url
                    embed.set_thumbnail(url=image)
                else:
                    await ctx.send("You need to send a thumbnail to add to the embed.")
                    return

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="timestamp")
    async def embed_timestamp(self, ctx, *, time: str):
        if ctx.author in self.embeds:
            try:
                timestamp = parser.parse(time).replace(tzinfo=None).astimezone(tz=timezone.utc)
            except parser.ParserError:
                await ctx.send("Failed to parse the time \"" + time + "\"")

            embed = self.embeds[ctx.author].embeds[0]
            embed.timestamp = timestamp

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="title")
    async def embed_title(self, ctx, *, title: str):
        if ctx.author in self.embeds:
            if len(title) > 256:
                await ctx.send("Title is too long! (Max 256 characters)")
                return

            embed = self.embeds[ctx.author].embeds[0]
            embed.title = title

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="url")
    async def embed_url(self, ctx, url: str):
        if ctx.author in self.embeds:
            embed = self.embeds[ctx.author].embeds[0]
            embed.url = url

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    # Fields

    @embed.command(pass_context=True, name="addField")
    async def add_field(self, ctx, title: str, *, value: str):
        if ctx.author in self.embeds:
            if len(title) > 256:
                await ctx.send("Title is too long! (Max 256 characters)")
                return
            elif len(value) > 1024:
                await ctx.send("Value is too long! (Max 1024 characters)")
                return

            embed = self.embeds[ctx.author].embeds[0]
            embed.add_field(name=title, value=value)

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()

    @embed.command(pass_context=True, name="removeField")
    async def remove_field(self, ctx, number: int):
        if ctx.author in self.embeds:
            embed = self.embeds[ctx.author].embeds[0]
            if len(embed.fields) <= number:
                embed.remove_field(number - 1)
                await self.embeds[ctx.author].edit(embed=embed)
                await ctx.message.delete()

    # Functions

    @embed.command(pass_context=True, name="reset")
    async def embed_reset(self, ctx):
        if ctx.author in self.embeds:
            await self.embeds[ctx.author].edit(embed=discord.Embed())
            await ctx.message.delete()

    @embed.command(pass_context=True, name="remove")
    async def embed_remove(self, ctx, attribute: str):
        if ctx.author in self.embeds:
            a = attribute.lower()
            embed = self.embeds[ctx.author].embeds[0]

            if "author" in a:
                embed.remove_author()
            elif "colour" in a or "color" in a:
                embed.colour = discord.Embed.Empty
            elif "description" in a:
                embed.description = discord.Embed.Empty
            elif "footer" in a:
                embed.set_footer(text=discord.Embed.Empty)
            elif "image" in a:
                embed.set_image(url=discord.Embed.Empty)
            elif "thumbnail" in a:
                embed.set_thumbnail(url=discord.Embed.Empty)
            elif "timestamp" in a:
                embed.timestamp = discord.Embed.Empty
            elif "title" in a:
                embed.title = discord.Embed.Empty
            elif "url" in a:
                embed.url = discord.Embed.Empty

            else:
                await ctx.send("Not a recognized attribute")
                return

            await self.embeds[ctx.author].edit(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="send")
    async def embed_send(self, ctx, channel: discord.TextChannel):
        if ctx.author in self.embeds:
            embed = self.embeds[ctx.author].embeds[0]
            message = await channel.send(embed=embed)
            del self.embeds[ctx.author]
            await ctx.send("Successfully sent embed (<" + message.jump_url + ">)")
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="done")
    async def embed_done(self, ctx):
        if ctx.author in self.embeds:
            await self.embeds[ctx.author].edit(content=None)
            del self.embeds[ctx.author]
            await ctx.send("Successfully completed embed")
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")

    @embed.command(pass_context=True, name="cancel")
    async def embed_cancel(self, ctx):
        if ctx.author in self.embeds:
            await self.embeds[ctx.author].delete()
            del self.embeds[ctx.author]
            await ctx.send("Successfully cancelled embed creation")
        else:
            await ctx.send("No embed is being worked on currently. To create one use `.embed create`.")


def setup(bot):
    bot.add_cog(EmbedBuilder(bot))
