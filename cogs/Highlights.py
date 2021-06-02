from cogs.Permissions import dm_commands
from discord.ext import commands
from datetime import datetime
from config import Config

import discord
import typing
import regex


class Highlights(commands.Cog):
    """
    Highlights cog to alert users when keywords of interest are said in a server
    """
    def __init__(self, bot):
        self.bot = bot
        self.highlights = Config.load_highlights()

    @commands.group(case_insensitive=True, aliases=["hl"])
    @commands.check(dm_commands)
    async def highlight(self, ctx):
        """
        Top level command for highlights

        :param ctx: Context object
        """
        if not ctx.invoked_subcommand:
            embed = discord.Embed(
                title="Highlight Commands",
                description=f".highlight add <keyword>\n"
                            f".highlight remove <keyword>\n"
                            f".highlight block <User/Channel>\n"
                            f".highlight unblock <User/Channel>\n"
                            f".highlight test <phrase>\n"
                            f".highlight list\n"
                            f".highlight clear\n",
                colour=discord.Colour(0x8899d4)
            )
            await ctx.send(embed=embed)

    @highlight.command(name="test", aliases=["t"])
    async def highlight_test(self, ctx, *, phrase):
        """
        Tests to see if a highlight will trigger with given phrase

        :param ctx: Context Object
        :param phrase: String to test
        """
        for keyword in self.highlights[str(ctx.author.id)]["keywords"]:
            if regex.search(keyword, phrase.lower()):
                await ctx.send(f"This phrase triggers the keyword \"{keyword}\"")
                return

        await ctx.send("This phrase did not trigger any of your keywords")

    @highlight.command(name="add", aliases=["a"])
    async def highlight_add(self, ctx, *, keyword):
        """
        Adds a keyword that a member wants to highlight

        :param ctx: Context object
        :param keyword: Keyword to add to the highlighters list
        """
        if str(ctx.author.id) not in self.highlights:
            self.highlights[str(ctx.author.id)] = {
                "keywords": [],
                "blocked_channels": [],
                "blocked_users": []
            }
        elif keyword.lower() in self.highlights[str(ctx.author.id)]:
            await ctx.send(
                f"You already have \"{keyword}\" as a highlight",
                allowed_mentions=discord.AllowedMentions.none()
            )
            return

        self.highlights[str(ctx.author.id)]["keywords"].append(keyword)
        Config.save_highlights(self.highlights)
        await ctx.send(
            f"Successfully added \"{keyword}\" as a highlight",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @highlight.command(name="remove", aliases=["r"])
    async def highlight_remove(self, ctx, *, keyword: str):
        """
        Removes a keyword that a member has for highlights

        :param ctx: Context object
        :param keyword: The keyword to remove or the # of the highlight
        """
        if str(ctx.author.id) not in self.highlights:
            await ctx.send("You don't have any highlights to remove")
            return
        elif keyword not in self.highlights[str(ctx.author.id)]["keywords"]:
            await ctx.send(
                "Did not find \"{keyword}\" in your highlights",
                allowed_mentions=discord.AllowedMentions.none()
            )

        self.highlights[str(ctx.author.id)]["keywords"].remove(keyword)
        Config.save_highlights(self.highlights)
        await ctx.send(
            f"Successfully removed \"{keyword}\" as a highlight",
            allowed_mentions=discord.AllowedMentions.none()
        )

    @highlight.command(name="list", aliases=["l"])
    async def highlight_list(self, ctx):
        """
        Sends a list of current highlights the user has

        :param ctx: Context object
        """
        embed = discord.Embed(
            title="Highlights",
            colour=discord.Colour(0x8899d4)
        )

        if str(ctx.author.id) not in self.highlights:
            embed.add_field(name="Keywords", value="None")
            embed.add_field(name="Blocked Channels", value="None")
            embed.add_field(name="Blocked Users", value="None")
        else:
            channels = []
            for channel_id in self.highlights[str(ctx.author.id)]["blocked_channels"]:
                channel = Config.main_guild.get_channel(channel_id)

                if channel is None:
                    continue

                channels.append(channel.mention)

            users = []
            for user_id in self.highlights[str(ctx.author.id)]["blocked_users"]:
                user = Config.main_guild.get_member(user_id)
                if user is None:
                    user = self.bot.fetch_user(user_id)

                users.append(user.mention)

            if len(self.highlights[str(ctx.author.id)]["keywords"]) == 0:
                embed.add_field(
                    name="Keywords",
                    value="None"
                )
            else:
                embed.add_field(
                    name="Keywords",
                    value="\n".join([x for x in self.highlights[str(ctx.author.id)]["keywords"]])
                )
            if len(channels) == 0:
                embed.add_field(
                    name="Blocked Channels",
                    value="None"
                )
            else:
                embed.add_field(
                    name="Blocked Channels",
                    value="\n".join(channels)
                )
            if len(users) == 0:
                embed.add_field(
                    name="Blocked Users",
                    value="None"
                )
            else:
                embed.add_field(
                    name="Blocked Users",
                    value="\n".join(users)
                )

        await ctx.send(embed=embed)

    @highlight.command(name="block", aliases=["b"])
    async def highlight_block(self, ctx, target: typing.Union[discord.TextChannel, discord.Member, discord.User]):
        """
        Blocks target channels and users from triggering highlights

        :param ctx: Context object
        :param target: Target object to block
        """
        if isinstance(target, discord.TextChannel):
            if target.id in self.highlights[str(ctx.author.id)]["blocked_channels"]:
                await ctx.send(f"You've already blocked {target.mention} from triggering highlights")
                return

            if target.guild != Config.main_guild:
                await ctx.send(f"Highlights only work in the {target.guild.name}")
                return

            self.highlights[str(ctx.author.id)]["blocked_channels"].append(target.id)
            Config.save_highlights(self.highlights)
            await ctx.send(f"Successfully blocked {target.mention}")
        else:
            if target.id in self.highlights[str(ctx.author.id)]["blocked_users"]:
                await ctx.send(
                    f"You've already blocked {target.mention} from triggering highlights",
                    allowed_mentions=discord.AllowedMentions.none()
                )
                return

            if target.id == ctx.author.id:
                await ctx.send(f"You can't block yourself")
                return

            self.highlights[str(ctx.author.id)]["blocked_users"].append(target.id)
            Config.save_highlights(self.highlights)
            await ctx.send(
                f"Successfully blocked {target.mention} from triggering highlights",
                allowed_mentions=discord.AllowedMentions.none()
            )

    @highlight.command(name="unblock", aliases=["ub"])
    async def highlight_unblock(self, ctx, target: typing.Union[discord.TextChannel, discord.Member, discord.User]):
        """
        Unblocks target channels and users from triggering highlights

        :param ctx: Context object
        :param target: Target object to unblock
        """
        if isinstance(target, discord.TextChannel):
            if target.id not in self.highlights[str(ctx.author.id)]["blocked_channels"]:
                await ctx.send(f"You haven't blocked {target.mention} from triggering highlights")
                return

            if target.guild != Config.main_guild:
                await ctx.send(f"Highlights only work in the {target.guild.name}")
                return

            self.highlights[str(ctx.author.id)]["blocked_channels"].remove(target.id)
            Config.save_highlights(self.highlights)
            await ctx.send(f"Successfully unblocked {target.mention}")
        else:
            if target.id not in self.highlights[str(ctx.author.id)]["blocked_users"]:
                await ctx.send(
                    f"You haven't blocked {target.mention} from triggering highlights",
                    allowed_mentions=discord.AllowedMentions.none()
                )
                return

            self.highlights[str(ctx.author.id)]["blocked_users"].remove(target.id)
            Config.save_highlights(self.highlights)
            await ctx.send(
                f"Successfully unblocked {target.mention} from triggering highlights",
                allowed_mentions=discord.AllowedMentions.none()
            )

    @highlight.command(name="clear", aliases=["c"])
    async def highlight_clear(self, ctx):
        """
        Clears the highlight settings

        :param ctx: Context object
        """
        self.highlights[str(ctx.author.id)]["keywords"] = []
        self.highlights[str(ctx.author.id)]["blocked_channels"] = []
        self.highlights[str(ctx.author.id)]["blocked_users"] = []

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Checks to see if any highlights were triggered

        :param message:
        """
        if message.author.bot or message.guild != Config.main_guild:
            return

        for user_id in self.highlights:
            if self.blocked(message, user_id):
                continue

            member = Config.main_guild.get_member(int(user_id))
            if member is None:
                continue

            for keyword in self.highlights[user_id]["keywords"]:
                if regex.search(keyword, message.content.lower()):
                    permissions = message.channel.permissions_for(member)
                    if permissions.view_channel and permissions.read_messages:
                        messages = await message.channel.history(
                            limit=4,
                            before=message.created_at,
                        ).flatten()
                        messages.reverse()
                        messages.append(message)

                        description = ""
                        for msg in messages:
                            description += f"**{msg.author.display_name}:** {msg.content}\n"

                        embed = discord.Embed(
                            title="Highlighted Message",
                            description=description + "\n[Go To](" + message.jump_url + ")",
                            colour=discord.Colour(0x8899d4)
                        )
                        embed.timestamp = datetime.now()

                        await member.send(
                            f"Your highlight \"{keyword}\" was triggered in the WPI Discord Server",
                            embed=embed
                        )
                        break

    def blocked(self, message, user_id):
        """
        Checks to see if a user has blocked sent message

        :param message: Message to check
        :param user_id: User to check blocks for
        """
        return message.channel.id in self.highlights[user_id]["blocked_channels"] or \
               message.author.id in self.highlights[user_id]["blocked_users"] or \
               message.author.id == int(user_id)


def setup(bot):
    bot.add_cog(Highlights(bot))
