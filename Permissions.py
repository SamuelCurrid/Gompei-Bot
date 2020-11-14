import discord

moderator_id = 742118136458772551

# Command channels
channels = [567179438047887381, 594579572855537765, 576475633870307330]


def administrator_perms(ctx):
    return ctx.message.author.guild_permissions.administrator


def moderator_perms(ctx):
    return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == moderator_id


def command_channels(ctx):
    return ctx.channel.id in channels


def dm_commands(ctx):
    return type(ctx.message.channel) is discord.DMChannel or command_channels(ctx)
