from config import Config
import discord


moderator_id = 742118136458772551


def administrator_perms(ctx):
    return ctx.message.author.guild_permissions.administrator


def moderator_perms(ctx):
    return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == moderator_id


def command_channels(ctx):
    return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == moderator_id or ctx.channel in Config.command_channels


def dm_commands(ctx):
    if isinstance(ctx.message.author, discord.User):
        return type(ctx.message.channel) is discord.DMChannel or command_channels(ctx)
    else:
        return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == moderator_id or type(ctx.message.channel) is discord.DMChannel or command_channels(ctx)


def owner(ctx):
    return ctx.message.author.id == Config.client.owner_id

