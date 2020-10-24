from GompeiFunctions import load_json, save_json
from Permissions import moderator_perms
from discord.ext import commands

import discord
import os


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_messages = {}
        self.load_reaction_message = load_json(os.path.join("config", "reaction_messages.json"))

    @commands.check(moderator_perms)
    @commands.command(pass_context=True, aliases=['rradd'])
    async def add_reaction_role(self, ctx, message_link, role_id, emoji):
        message_id = int(message_link[message_link.rfind("/") + 1:])
        short_link = message_link[:message_link.rfind("/")]
        channel_id = int(short_link[short_link.rfind("/") + 1:])

        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("Not a valid link to message")
        else:
            message = await channel.fetch_message(message_id)
            if message is None:
                await ctx.send("Not a valid link to message")
            else:
                role = ctx.guild.get_role(int(role_id))

                if role is None:
                    await ctx.send("Not a valid role ID")
                else:
                    if ctx.message.author.top_role.position < role.position:
                        await ctx.send("You do not have permission to make a reaction role for this role")
                    else:
                        await message.add_reaction(emoji)

                        # Get a list of pre-existing reactions
                        reactions = [self.bot.user.id]
                        for reaction in message.reactions:
                            if type(reaction.emoji) is discord.Emoji:
                                emoji_name = "<:" + reaction.emoji.name + ":" + str(reaction.emoji.id) + ">"
                            else:
                                emoji_name = reaction.emoji

                            print(emoji_name + " vs. " + emoji)
                            if emoji_name == emoji:
                                print("got here")

                                async for user in reaction.users():
                                    reactions.append(user.id)
                                break

                        combined_id = str(channel_id) + str(message_id)

                        if combined_id in self.reaction_messages:
                            self.reaction_messages[combined_id][emoji] = {"id": role_id, "users": reactions}
                        else:
                            self.reaction_messages[combined_id] = {emoji: {"id": role_id, "users": reactions}}

                        save_json(os.path.join("config", "reaction_messages.json"), self.reaction_messages)
                        await ctx.send("Created reaction role")

    @commands.check(moderator_perms)
    @commands.command(pass_context=True, aliases=['rrdelete', 'rremove'])
    async def remove_reaction_role(self, ctx, message_link, emoji):
        message_id = int(message_link[message_link.rfind("/") + 1:])
        short_link = message_link[:message_link.rfind("/")]
        channel_id = int(short_link[short_link.rfind("/") + 1:])

        key = str(channel_id) + str(message_id)
        if key not in self.reaction_messages:
            await ctx.send("There are no reaction roles on this message")
        else:
            if emoji not in self.reaction_messages[key]:
                await ctx.send("This emoji is not used on this reaction role")
            else:
                del self.reaction_messages[key][emoji]
                save_json(os.path.join("config", "reaction_messages.json"), self.reaction_messages)
                channel = ctx.guild.get_channel(channel_id)
                message = await channel.fetch_message(message_id)

                await message.remove_reaction(emoji, self.bot.user)
                await ctx.send("Removed reaction role")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot:
            key = str(payload.channel_id) + str(payload.message_id)
            if key in self.reaction_messages:
                if str(payload.emoji) in self.reaction_messages[key]:
                    role_id = self.reaction_messages[key][str(payload.emoji)]["id"]
                    guild = self.bot.get_guild(567169726250352640)
                    role = guild.get_role(int(role_id))
                    member = payload.member
                    roles = member.roles
                    roles.append(role)

                    self.reaction_messages[key][str(payload.emoji)]["users"].append(member.id)
                    save_json(os.path.join("config", "reaction_messages.json"), self.reaction_messages)

                    await payload.member.edit(roles=roles)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        key = str(payload.channel_id) + str(payload.message_id)
        if key in self.reaction_messages:
            if str(payload.emoji) in self.reaction_messages[key]:
                role_id = self.reaction_messages[key][str(payload.emoji)]["id"]
                guild = self.bot.get_guild(567169726250352640)
                role = guild.get_role(int(role_id))

                channel = guild.get_channel(int(key[0:18]))
                message = await channel.fetch_message(int(key[18:]))

                for reaction in message.reactions:
                    if type(reaction.emoji) is discord.Emoji:
                        emoji_name = "<:" + reaction.emoji.name + ":" + str(reaction.emoji.id) + ">"

                    else:
                        emoji_name = reaction.emoji

                    if emoji_name == str(payload.emoji):

                        for user in self.reaction_messages[key][str(payload.emoji)]["users"]:
                            found = False
                            async for reacted in reaction.users():
                                if user == reacted.id:
                                    found = True
                                    break

                            if not found:
                                member = guild.get_member(user)
                                self.reaction_messages[key][str(payload.emoji)]["users"].remove(user)
                                if member is not None:
                                    await member.remove_roles(role)
