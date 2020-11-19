from GompeiFunctions import load_json, save_json

import discord
import os

settings = load_json(os.path.join("config", "settings.json"))


def set_guild(guild: discord.Guild):
    """
    Sets the guild to be used by the bot

    :param guild: Guild object
    """
    settings["guild_id"] = guild.id
    save_json(os.path.join("config", "settings"), settings)


def set_booster_role(role: discord.Role):
    """
    Sets the nitro booster role for the guild

    :param role: Role to set it to
    """
    settings["nitro_booster_id"] = role.id
    save_json(os.path.join("config", "settings"), settings)


def set_mod_log(channel: discord.TextChannel):
    """
    Sets the mod log channel for the bot

    :param channel:
    """
    settings["mod_log"] = channel.id
    save_json(os.path.join("config", "settings"), settings)


def set_status(client: discord.Client, status: str):
    """
    Sets the status for the bot

    :param client: Client to update
    :param status: String to use for the status
    """
    settings["status"] = status
    save_json(os.path.join("config", "settings"), settings)


def set_dm_channel(channel: discord.TextChannel):
    """
    Sets the DM channel

    :param channel: Channel to be used
    """
    settings["dm_channel_id"] = channel.id
    save_json(os.path.join("config", "settings"), settings)


def clear_dm_channel():
    """
    Clears the set DM channel
    """
    settings["dm_channel_id"] = None
    save_json(os.path.join("config", "settings"), settings)


def set_prefix(prefix: str):
    """
    Sets the prefix for the bot

    :param prefix: prefix to use
    """
    settings["prefix"] = prefix
    save_json(os.path.join("config", "settings"), settings)


def add_access_roles(*roles: discord.Role):
    """
    Adds access roles to the config

    :param roles: roles to add
    """
    for role in roles:
        settings["access_roles"].append(role.id)
    save_json(os.path.join("config", "settings"), settings)


def remove_access_roles(*roles: discord.Role):
    """
    Removes access roles from the config

    :param roles: roles to remove
    """
    for role in roles:
        settings["access_roles"].remove(role.id)
    save_json(os.path.join("config", "settings"), settings)


def clear_access_roles():
    """
    Clears access roles
    """
    settings["access_roles"] = []
    save_json(os.path.join("config", "settings"), settings)


def add_opt_in_roles(*roles: discord.Role):
    """
    Adds opt in roles

    :param roles: roles ot add
    """
    for role in roles:
        settings["opt_in_roles"].append(role.id)
    save_json(os.path.join("config", "settings"), settings)


def remove_opt_in_roles(*roles: discord.Role):
    """
    Removes opt in roles

    :param roles: roles to remove
    """
    for role in roles:
        settings["opt_in_roles"].remove(role.id)
    save_json(os.path.join("config", "settings"), settings)


def clear_opt_in_roles():
    """
    Clears opt-in roles
    """
    settings["access_roles"] = []
    save_json(os.path.join("config", "settings"), settings)
