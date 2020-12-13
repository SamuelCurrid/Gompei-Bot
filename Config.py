from GompeiFunctions import load_json, save_json
from datetime import datetime

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
    "staff": None,
    "last_audit": None,
    "invites": {}
}
administration = {
    "mutes": {},
    "jails": {}
}
close_time = None


async def set_client(new_client: discord.Client):
    global client
    client = new_client


async def load_settings():
    """
    Loads the settings with the client
    :return:
    """
    global raw_settings, client, guild, status, prefix, logging, close_time
    raw_settings = load_json(os.path.join("config", "settings.json"))

    prefix = raw_settings["prefix"]

    guild = client.get_guild(raw_settings["guild_id"])

    if raw_settings["close_time"] is not None:
        close_time = datetime.strptime(raw_settings["close_time"], "%Y-%m-%d %H:%M:%S")

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
    save_json(os.path.join("config", "settings.json"), raw_settings)


async def update_guild_settings():
    global dm_channel, logging, access_roles, opt_in_roles, administration

    update_nitro_role()

    dm_channel = guild.get_channel(raw_settings["dm_channel_id"])

    logging["channel"] = guild.get_channel(raw_settings["logging"]["channel"])

    for key in logging["overwrite_channels"]:
        logging["overwrite_channels"][key] = guild.get_channel(raw_settings["logging"]["overwrite_channels"][key])

    logging["last_audit"] = raw_settings["logging"]["last_audit"]
    logging["staff"] = guild.get_channel(raw_settings["logging"]["staff"])

    invites = await guild.invites()
    for invite in invites:
        add_invite(invite.code, invite.inviter.id, invite.uses)

    for role_id in raw_settings["access_roles"]:
        access_roles.append(guild.get_role(role_id))

    for role_id in raw_settings["opt_in_roles"]:
        opt_in_roles.append(guild.get_role(role_id))

    for user_id in raw_settings["administration"]["mutes"]:
        member = guild.get_member(user_id)

        # If user has left the server since last run, remove their mute
        if member is None:
            del user_id
            continue

        administration["mutes"][member] = datetime.strptime(raw_settings["administration"]["mutes"][user_id]["date"], "%Y-%m-%d %H:%M:%S")

    for user_id in raw_settings["administration"]["jails"]:
        member = guild.get_member(user_id)

        # If user has left the server since last run, remove their jail
        if member is None:
            del user_id
            continue

        roles = []
        for role_id in raw_settings["administration"]["jails"][user_id]["roles"]:
            # Check if the role exists
            if guild.get_role(role_id) is not None:
                roles.append(guild.get_role(role_id))

        lift_date = datetime.strptime(raw_settings["administration"]["jails"][user_id]["date"], "%Y-%m-%d %H:%M:%S")

        administration["jails"][member] = {"date": lift_date, "roles": roles}

    save_json(os.path.join("config", "settings.json"), raw_settings)


def update_nitro_role():
    global nitro_role

    for role in guild.roles:
        if role.name == "Nitro Booster":
            nitro_role = role
            raw_settings["nitro_booster_id"] = role.id


def set_mod_log(channel: discord.TextChannel):
    """
    Sets the mod log channel for the bot

    :param channel:
    """
    global logging, raw_settings

    logging["overwrite_channels"]["mod"] = channel
    raw_settings["logging"]["overwrite_channels"]["mod"] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_status(new_status: str):
    """
    Sets the status for the bot

    :param new_status: String to use for the status
    """
    global status, raw_settings

    status = raw_settings["status"] = new_status
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_dm_channel(channel: discord.TextChannel):
    """
    Sets the DM channel

    :param channel: Channel to be used
    """
    global dm_channel, raw_settings

    dm_channel = channel
    raw_settings["dm_channel_id"] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_dm_channel():
    """
    Clears the set DM channel
    """
    global dm_channel, raw_settings

    dm_channel = raw_settings["dm_channel_id"] = None
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_prefix(new_prefix: str):
    """
    Sets the prefix for the bot

    :param new_prefix: prefix to use
    """
    global prefix, raw_settings

    prefix = raw_settings["prefix"] = new_prefix
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_access_roles(*roles: discord.Role):
    """
    Adds access roles to the config

    :param roles: roles to add
    """
    global access_roles, raw_settings

    for role in roles:
        access_roles.append(role)
        raw_settings["access_roles"].append(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_access_roles(*roles: discord.Role):
    """
    Removes access roles from the config

    :param roles: roles to remove
    """
    global access_roles, raw_settings

    for role in roles:
        access_roles.remove(role)
        raw_settings["access_roles"].remove(role.id)

    save_json(os.path.join("config", "settings,json"), raw_settings)


def clear_access_roles():
    """
    Clears access roles
    """
    global access_roles, raw_settings

    access_roles = raw_settings["access_roles"] = []
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_opt_in_roles(*roles: discord.Role):
    """
    Adds opt in roles

    :param roles: Roles to add
    """
    global opt_in_roles, raw_settings

    for role in roles:
        opt_in_roles.append(role)
        raw_settings["opt_in_roles"].append(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_opt_in_roles(*roles: discord.Role):
    """
    Removes opt in roles

    :param roles: Roles to remove
    """
    global opt_in_roles, raw_settings

    for role in roles:
        opt_in_roles.remove(role)
        raw_settings["opt_in_roles"].remove(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_opt_in_roles():
    """
    Clears opt-in roles
    """
    global opt_in_roles, raw_settings

    opt_in_roles = raw_settings["access_roles"] = []
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_logging_channel(channel: discord.TextChannel):
    """
    Sets the logging channel

    :param channel: Channel to use
    """
    global logging, raw_settings

    logging["channel"] = channel
    raw_settings["logging"]["channel"] = channel.id

    for overwrite in logging["overwrite_channels"]:
        if logging["overwrite_channels"][overwrite] is None:
            logging["overwrite_channels"][overwrite] = channel
            raw_settings["logging"]["overwrite_channels"][overwrite] = channel.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_overwrite_logging_channel(logging_type: str, channel: discord.TextChannel):
    """
    Overwrites specific logging channels

    :param logging_type: The type of logging you want to overwrite
    :param channel: Channel to send logging messages to
    """
    global logging, raw_settings

    logging["overwrite_channels"][logging_type] = channel
    raw_settings["logging"]["overwrite_channels"][logging_type] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_last_audit(audit: str):
    """
    Sets the last audit

    :param audit: code for the last audit
    """
    global logging, raw_settings

    logging["last_audit"] = raw_settings["logging"]["last_audit"] = audit
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_invite(invite: str, user_id: int, uses: int):
    """
    Adds an invite

    :param invite: invite code
    :param user_id: user who created the invite
    :param uses: uses the invite has
    """
    global logging, raw_settings

    logging["invites"][invite] = raw_settings["logging"]["invites"][invite] = {
        "inviter_id": user_id,
        "uses": uses
    }
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_invite(invite: str):
    """
    Removes an invite

    :param invite: invite code
    """
    global logging, raw_settings

    del logging["invites"][invite]
    del raw_settings["logging"]["invites"]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def update_invite_uses(invite: str, uses: int):
    """
    Updates the amount of times an invite has been used

    :param invite: invite code
    :param uses: times used
    """
    global logging, raw_settings

    logging["invites"][invite]["uses"] = raw_settings["logging"]["invites"][invite]["uses"] = uses
    save_json(os.path.join("config", "settings.json"), raw_settings)


def automod_setting_enable(automod_type: str):
    """
    Enables automod settings

    :param automod_type: setting to enable
    """
    global automod, raw_settings

    automod[automod_type]["enabled"] = raw_settings["automod"][automod_type]["enabled"] = True
    save_json(os.path.join("config", "settings.json"), raw_settings)


def automod_setting_disable(automod_type: str):
    """
    Disabled automod settings

    :param automod_type: setting to disable
    """
    global automod, raw_settings

    automod[automod_type]["enabled"] = raw_settings["automod"][automod_type]["enabled"] = False
    save_json(os.path.join("config", "settings.json"), raw_settings)


def automod_set_message_rate_limit(number: int, seconds: int):
    global automod, raw_settings

    automod["message_rate"]["number"] = raw_settings["automod"]["message_rate"]["number"] = number
    automod["message_rate"]["seconds"] = raw_settings["automod"]["message_rate"]["seconds"] = seconds
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_mute(member: discord.Member, date: datetime):
    administration["mutes"][member] = {"date": date}
    raw_settings["administration"]["mutes"][member.id] = {"date": date.strftime("%Y-%m-%d %H:%M:%S")}
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_mute(member: discord.Member):
    del administration["mutes"][member]
    del raw_settings["administration"]["mutes"][member.id]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_jail(member: discord.Member, date: datetime, roles):
    role_ids = []
    for role in roles:
        role_ids.append(role.id)

    administration["jails"][member] = {"date": date, "roles": roles}
    raw_settings["administration"]["jails"][member.id] = {"date": date.strftime("%Y-%m-%d %H:%M:%S"), "roles": role_ids}
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_jail(member: discord.Member):
    del administration["jails"][member]
    del raw_settings["administration"]["jails"][member.id]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_staff_channel(channel: discord.TextChannel):
    global logging, raw_settings

    logging["staff"] = channel
    raw_settings["logging"]["staff"] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_staff_channel():
    global logging, raw_settings

    logging["staff"] = raw_settings["logging"]["staff"] = None
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_close_time():
    global close_time, raw_settings

    close_time = datetime.now()
    raw_settings["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_close_time():
    global close_time, raw_settings

    close_time = raw_settings["close_time"] = None
    save_json(os.path.join("config", "settings.json"), raw_settings)
