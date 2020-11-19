from GompeiFunctions import load_json, save_json

import discord
import os

raw_settings = None
client = None

guild = None
nitro_role = None
status = None
dm_channel = None
prefix = None
access_roles = []
opt_in_roles = []
logging = {
    "channel": None,
    "overwrite_channels": {
        "member": None,
        "message": None,
        "member_tracking": None,
        "mod": None,
        "server": None,
        "status": None,
        "voice": None
    },
    "last_audit": None,
    "invites": {}
}


async def set_client(new_client: discord.Client):
    global client
    client = new_client


async def load_settings():
    """
    Loads the settings with the client
    :return:
    """
    global raw_settings, client, guild, status, prefix, logging
    raw_settings = load_json(os.path.join("config", "settings.json"))

    prefix = raw_settings["prefix"]

    guild = client.get_guild(raw_settings["guild_id"])

    if guild is not None:
        await update_guild_settings()

    status = raw_settings["status"]
    if status is not None:
        await client.change_presence(activity=discord.Game(name=status))


async def set_guild(new_guild: discord.Guild):
    """
    Sets the guild to be used by the bot

    :param new_guild: Guild object
    """
    global guild

    guild = new_guild

    await update_guild_settings()

    raw_settings["guild_id"] = guild.id
    save_json(os.path.join("config", "settings"), raw_settings)


async def update_guild_settings():
    global dm_channel, logging, access_roles, opt_in_roles

    update_nitro_role()

    dm_channel = guild.get_channel(raw_settings["dm_channel_id"])

    logging["channel"] = guild.get_channel(raw_settings["logging"]["channel"])

    for key in logging["overwrite_channels"]:
        logging["overwrite_channels"][key] = guild.get_channel(raw_settings["logging"]["overwrite_channels"][key])

    logging["last_audit"] = raw_settings["logging"]["last_audit"]
    logging["invites"] = raw_settings["logging"]["invites"]

    for role_id in raw_settings["access_roles"]:
        access_roles.append(guild.get_role(role_id))

    for role_id in raw_settings["opt_in_roles"]:
        opt_in_roles.append(guild.get_role(role_id))


def update_nitro_role():
    global nitro_role

    for role in guild.roles:
        if role.name == "Nitro Booster":
            if raw_settings["nitro_booster_id"] != role.id:
                nitro_role = role
                raw_settings["nitro_booster_id"] = role.id


def set_mod_log(channel: discord.TextChannel):
    """
    Sets the mod log channel for the bot

    :param channel:
    """
    global logging, raw_settings

    logging["overwrite_channels"]["mod"] = channel
    raw_settings["mod"] = channel.id
    save_json(os.path.join("config", "settings"), raw_settings)


def set_status(new_status: str):
    """
    Sets the status for the bot

    :param client: Client to update
    :param status: String to use for the status
    """
    global status, raw_settings

    status = raw_settings["status"] = new_status
    save_json(os.path.join("config", "settings"), raw_settings)


def set_dm_channel(channel: discord.TextChannel):
    """
    Sets the DM channel

    :param channel: Channel to be used
    """
    global dm_channel, raw_settings

    dm_channel = channel
    raw_settings["dm_channel_id"] = channel.id
    save_json(os.path.join("config", "settings"), raw_settings)


def clear_dm_channel():
    """
    Clears the set DM channel
    """
    global dm_channel, raw_settings

    dm_channel = raw_settings["dm_channel_id"] = None
    save_json(os.path.join("config", "settings"), raw_settings)


def set_prefix(new_prefix: str):
    """
    Sets the prefix for the bot

    :param prefix: prefix to use
    """
    global prefix, raw_settings

    prefix = raw_settings["prefix"] = new_prefix
    save_json(os.path.join("config", "settings"), raw_settings)


def add_access_roles(*roles: discord.Role):
    """
    Adds access roles to the config

    :param roles: roles to add
    """
    global access_roles, raw_settings

    for role in roles:
        access_roles.append(role)
        raw_settings["access_roles"].append(role.id)

    save_json(os.path.join("config", "settings"), raw_settings)


def remove_access_roles(*roles: discord.Role):
    """
    Removes access roles from the config

    :param roles: roles to remove
    """
    global access_roles, raw_settings

    for role in roles:
        access_roles.remove(role)
        raw_settings["access_roles"].remove(role.id)

    save_json(os.path.join("config", "settings"), raw_settings)


def clear_access_roles():
    """
    Clears access roles
    """
    global access_roles, raw_settings

    access_roles = raw_settings["access_roles"] = []
    save_json(os.path.join("config", "settings"), raw_settings)


def add_opt_in_roles(*roles: discord.Role):
    """
    Adds opt in roles

    :param roles: roles ot add
    """
    global opt_in_roles, raw_settings

    for role in roles:
        opt_in_roles.append(role)
        raw_settings["opt_in_roles"].append(role.id)

    save_json(os.path.join("config", "settings"), raw_settings)


def remove_opt_in_roles(*roles: discord.Role):
    """
    Removes opt in roles

    :param roles: roles to remove
    """
    global opt_in_roles, raw_settings

    for role in roles:
        opt_in_roles.remove(role)
        raw_settings["opt_in_roles"].remove(role.id)

    save_json(os.path.join("config", "settings"), raw_settings)


def clear_opt_in_roles():
    """
    Clears opt-in roles
    """
    global opt_in_roles, raw_settings

    opt_in_roles = raw_settings["access_roles"] = []
    save_json(os.path.join("config", "settings"), raw_settings)


def set_logging_channel(channel: discord.TextChannel):
    global logging, raw_settings

    logging["channel"] = channel
    raw_settings["logging"]["channel"] = channel.id

    for overwrite in logging["overwrite_channels"]:
        if logging["overwrite_channels"][overwrite] is None:
            logging["overwrite_channels"][overwrite] = channel
            raw_settings["logging"]["overwrite_channels"][overwrite] = channel.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_overwrite_logging_channel(logging_type: str, channel: discord.TextChannel):
    global logging, raw_settings

    logging["overwrite_channels"][logging_type] = channel
    raw_settings["logging"]["overwrite_channels"][logging_type] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_last_audit(audit: str):
    global logging, raw_settings

    logging["last_audit"] = raw_settings["logging"]["last_audit"] = audit
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_invite(invite: str, user_id: int, uses: int):
    global logging, raw_settings

    logging["invites"][invite] = raw_settings["logging"]["invites"] = {
        "inviter_id": user_id,
        "uses": uses
    }
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_invite(invite: str):
    global logging, raw_settings

    del logging["invites"][invite]
    del raw_settings["logging"]["invites"]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def update_invite_uses(invite: str, uses: int):
    global logging, raw_settings

    logging["invites"][invite]["uses"] = raw_settings["logging"]["invites"][invite]["uses"] = invite.uses
    save_json(os.path.join("config", "settings.json"), raw_settings)
