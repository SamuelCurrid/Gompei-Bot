# Mod role ID
moderator_id = 742118136458772551

# Command channels
command_channels = [567179438047887381, 594579572855537765, 576475633870307330]


def administrator_perms(ctx):
	return ctx.message.author.guild_permissions.administrator


def moderator_perms(ctx):
	return ctx.message.author.guild_permissions.administrator or ctx.message.author.top_role.id == moderator_id


def command_channels(ctx):
	return ctx.channel.id in command_channels
