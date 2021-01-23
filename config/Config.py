from GompeiFunctions import load_json, save_json
from datetime import datetime

import discord
import pickle
import os

client = None
close_time = None
dm_channel = None
lockouts = {}
main_guild = None
prefix = "."
raw_settings = None
status = None
guilds = {}


async def set_client(new_client: discord.Client):
    global client
    client = new_client


async def load_settings():
    """
    Loads the settings with the client
    :return:
    """
    global client, close_time, dm_channel, main_guild, prefix, raw_settings, status, guilds
    raw_settings = load_json(os.path.join("config", "settings.json"))

    prefix = raw_settings["prefix"]

    main_guild = client.get_guild(raw_settings["main_guild"])

    if raw_settings["close_time"] is not None:
        close_time = datetime.strptime(raw_settings["close_time"], "%Y-%m-%d %H:%M:%S")

    if main_guild is not None:
        await update_main_guild_settings()

    status = raw_settings["status"]
    if status is not None:
        await client.change_presence(activity=discord.Game(name=status))

    for guild in client.guilds:
        if str(guild.id) in raw_settings["guilds"]:
            await update_guild_settings(guild)
        else:
            add_guild(guild)


async def set_main_guild(new_guild: discord.Guild):
    """
    Sets the guild to be used by the bot

    :param new_guild: Guild object
    """
    global main_guild, raw_settings

    main_guild = new_guild
    raw_settings["main_guild"] = main_guild.id

    print(main_guild)
    print(raw_settings)

    await update_main_guild_settings()

    save_json(os.path.join("config", "settings.json"), raw_settings)


async def update_main_guild_settings():
    """
    Updates guild settings for the currently selected guild
    """
    global dm_channel, lockouts, main_guild

    dm_channel = main_guild.get_channel(raw_settings["dm_channel_id"])

    for user_id in list(raw_settings["lockouts"]):
        member = main_guild.get_member(int(user_id))

        if member is None:
            del raw_settings["lockouts"][user_id]
            continue

        roles = []
        for role_id in raw_settings["lockouts"][user_id]:
            role = main_guild.get_role(role_id)
            if role is not None:
                roles.append(role)

        lockouts[member] = roles


async def update_guild_settings(guild: discord.Guild):
    """
    Updates guild settings for guilds
    """
    global guilds

    guilds[guild] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "opt_in_roles": [],
        "announcement_channels": [],
        "command_channels": [],
        "muted_role": None,
        "logging": {
            "channel": None,
            "overwrite_channels": {
                "avatar": None,
                "member": None,
                "message": None,
                "member_tracking": None,
                "mod": None,
                "reaction": None,
                "server": None,
                "status": None,
                "voice": None
            },
            "staff": None,
            "last_audit": None,
            "invites": {}
        },
        "administration": {
            "mutes": {},
            "jails": {}
        }
    }

    update_nitro_role(guild)

    for key in guilds[guild]["logging"]["overwrite_channels"]:
        guilds[guild]["logging"]["overwrite_channels"][key] = \
            guild.get_channel(raw_settings["guilds"][str(guild.id)]["logging"]["overwrite_channels"][key])

    for channel_id in raw_settings["guilds"][str(guild.id)]["command_channels"]:
        channel = guild.get_channel(channel_id)

        if channel is None:
            raw_settings["guilds"][str(guild.id)]["command_channels"].remove(channel_id)
        else:
            guilds[guild]["command_channels"].append(channel)

    guilds[guild]["logging"]["last_audit"] = (await guild.audit_logs(limit=1).flatten())[0].id
    guilds[guild]["logging"]["staff"] = guild.get_channel(raw_settings["guilds"][str(guild.id)]["logging"]["staff"])
    for invite in await guild.invites():
        guilds[guild]["logging"]["invites"][invite] = {
            "inviter_id": invite.inviter.id,
            "uses": invite.uses
        }

    for role_id in raw_settings["guilds"][str(guild.id)]["access_roles"]:
        guilds[guild]["access_roles"].append(guild.get_role(role_id))

    for role_id in raw_settings["guilds"][str(guild.id)]["opt_in_roles"]:
        guilds[guild]["opt_in_roles"].append(guild.get_role(role_id))

    for user_id in raw_settings["guilds"][str(guild.id)]["administration"]["mutes"]:
        member = guild.get_member(user_id)

        # If user has left the server since last run, remove their mute
        if member is None:
            del user_id
            continue

        guilds[guild]["administration"]["mutes"][member] = datetime.strptime(
            raw_settings["guilds"][str(guild.id)]["administration"]["mutes"][user_id]["date"],
            "%Y-%m-%d %H:%M:%S"
        )

    for user_id in raw_settings["guilds"][str(guild.id)]["administration"]["jails"]:
        member = guild.get_member(user_id)

        # If user has left the server since last run, remove their jail
        if member is None:
            del user_id
            continue

        roles = []
        for role_id in raw_settings["guilds"][str(guild.id)]["administration"]["jails"][user_id]["roles"]:
            # Check if the role exists
            if guild.get_role(role_id) is not None:
                roles.append(guild.get_role(role_id))

        lift_date = datetime.strptime(
            raw_settings["guilds"][str(guild.id)]["administration"]["jails"][user_id]["date"],
            "%Y-%m-%d %H:%M:%S"
        )

        guilds[guild]["administration"]["jails"][member] = {"date": lift_date, "roles": roles}

    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_guild(guild: discord.Guild):
    global guilds, raw_settings

    guilds[guild] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "opt_in_roles": [],
        "command_channels": [],
        "muted_role": None,
        "logging": {
            "channel": None,
            "overwrite_channels": {
                "avatar": None,
                "member": None,
                "message": None,
                "member_tracking": None,
                "mod": None,
                "reaction": None,
                "server": None,
                "status": None,
                "voice": None
            },
            "staff": None,
            "last_audit": None,
            "invites": {}
        },
        "administration": {
            "mutes": {},
            "jails": {}
        }
    }

    raw_settings["guilds"][str(guild.id)] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "opt_in_roles": [],
        "command_channels": [],
        "muted_role": None,
        "logging": {
            "channel": None,
            "overwrite_channels": {
                "avatar": None,
                "member": None,
                "message": None,
                "member_tracking": None,
                "mod": None,
                "reaction": None,
                "server": None,
                "status": None,
                "voice": None
            },
            "staff": None,
            "invites": {}
        },
        "administration": {
            "mutes": {},
            "jails": {}
        }
    }

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_guild(guild: discord.Guild):
    global guilds, raw_settings

    guilds.remove(guild)
    del raw_settings["guilds"][(str(guild.id))]


def update_nitro_role(guild: discord.Guild):
    """
    Updates the nitro role for the guild

    :param guild: Guild to update
    """
    global guilds

    for role in guild.roles:
        if role.name == "Nitro Booster":
            guilds[guild]["nitro_role"] = role
            raw_settings["guilds"][str(guild.id)]["nitro_role"] = role.id


def set_logging_channel(type: str, channel: discord.TextChannel):
    """
    Sets the logging channel for the bot

    :param type: Type of logging channel to set
    :param channel: Channel to use for logging
    """
    global guilds, raw_settings

    guilds[channel.guild]["logging"]["overwrite_channels"][type] = channel
    raw_settings["guilds"][str(channel.guild.id)]["logging"]["overwrite_channels"][type] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_logging_channels(channel: discord.TextChannel):
    """
    Sets all logging channels to a singular one

    :param channel: Channel to send logging messages to
    """
    global guilds, raw_settings

    for overwrite in guilds[channel.guild]["logging"]["overwrite_channels"].keys():
        guilds[channel.guild]["logging"]["overwrite_channels"][overwrite] = channel
        raw_settings["guilds"][str(channel.guild.id)]["logging"]["overwrite_channels"][overwrite] = channel.id

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

    :param new_prefix: Prefix to use
    """
    global prefix, raw_settings

    prefix = raw_settings["prefix"] = new_prefix
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_guild_prefix(guild: discord.Guild, new_prefix: str):
    """
    Sets the prefix for a guild

    :param guild:
    :param new_prefix: Prefix to use
    """
    global guilds, raw_settings

    guilds[guild]["prefix"] = raw_settings["guilds"][str(guild.id)]["prefix"] = new_prefix


def add_access_roles(*roles: discord.Role):
    """
    Adds access roles to the config

    :param roles: Roles to add
    """
    global guilds, raw_settings

    for role in roles:
        guilds[role.guild]["access_roles"].append(role)
        raw_settings["guilds"][str(role.guild.id)]["access_roles"].append(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_access_roles(*roles: discord.Role):
    """
    Removes access roles from the config

    :param roles: Roles to remove
    """
    global guilds, raw_settings

    for role in roles:
        guilds[role.guild]["access_roles"].remove(role)
        raw_settings["guilds"][str(role.guild.id)]["access_roles"].remove(role.id)

    save_json(os.path.join("config", "settings,json"), raw_settings)


def clear_access_roles(guild: discord.Guild):
    """
    Clears access roles

    :param guild: Guild to clear access roles for
    """
    global guilds, raw_settings

    guilds[guild]["access_roles"] = raw_settings["guilds"][str(guild.id)]["access_roles"] = []
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_opt_in_roles(*roles: discord.Role):
    """
    Adds opt in roles

    :param roles: Roles to add
    """
    global guilds, raw_settings

    for role in roles:
        guilds[role.guild]["opt_in_roles"].append(role)
        raw_settings["guilds"][role.guild]["opt_in_roles"].append(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_opt_in_roles(*roles: discord.Role):
    """
    Removes opt in roles

    :param roles: Roles to remove
    """
    global guilds, raw_settings

    for role in roles:
        guilds[role.guild]["opt_in_roles"].remove(role)
        raw_settings["guilds"][str(role.guild.id)]["opt_in_roles"].remove(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_opt_in_roles(guild: discord.Guild):
    """
    Clears opt-in roles

    :param guild: Guild to clear opt-in roles for
    """
    global guilds, raw_settings

    guilds[guild]["opt_in_roles"] = raw_settings["guilds"][str(guild.id)]["access_roles"] = []
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_logging_channel(channel: discord.TextChannel):
    """
    Sets the logging channel

    :param channel: Channel to use
    """
    global guilds, raw_settings

    guilds[channel.guild]["logging"]["channel"] = channel
    raw_settings["guilds"][str(channel.guild.id)]["logging"]["channel"] = channel.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_all_logging_channels(channel: discord.TextChannel):
    """
    Sets all logging channels/overwrites

    :param channel: Channel to send logging messages to
    """
    global guilds, raw_settings

    set_logging_channel(channel)

    for overwrite in guilds[channel.guild]["logging"]["overwrite_channels"]:
        if guilds[channel.guild]["logging"]["overwrite_channels"][overwrite] is None:
            guilds[channel.guild]["logging"]["overwrite_channels"][overwrite] = channel
            raw_settings["guilds"][str(channel.guild.id)]["logging"]["overwrite_channels"][overwrite] = channel.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_overwrite_logging_channel(logging_type: str, channel: discord.TextChannel):
    """
    Overwrites specific logging channels

    :param logging_type: The type of logging you want to overwrite
    :param channel: Channel to send logging messages to
    """
    global guilds, raw_settings

    guilds[channel.guild]["logging"]["overwrite_channels"][logging_type] = channel
    raw_settings["guilds"][str(channel.guild.id)]["logging"]["overwrite_channels"][logging_type] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_last_audit(audit: discord.AuditLogEntry):
    """
    Sets the last audit

    :param audit: Last audit log entry
    """
    global guilds, raw_settings

    guilds[audit.guild]["logging"]["last_audit"] = audit.id


def add_invite(invite: discord.Invite):
    """
    Adds an invite

    :param invite: Invite code
    """
    global guilds, raw_settings

    guilds[invite.guild]["logging"]["invites"][invite.code] = {
        "inviter_id": invite.inviter.id,
        "uses": invite.inviter.id
    }


def remove_invite(invite: discord.Invite):
    """
    Removes an invite

    :param invite: Invite code
    """
    global guilds, raw_settings

    del guilds[invite.guild]["logging"]["invites"][invite.code]


def update_invite_uses(invite: discord.Invite):
    """
    Updates the amount of times an invite has been used

    :param invite: invite code
    """
    global guilds, raw_settings

    guilds[invite.guild]["logging"]["invites"][invite]["uses"] = discord.Invite.uses


def add_mute(member: discord.Member, date: datetime):
    """
    Adds a muted user

    :param member: Member to add
    :param date: Date mute expires
    """
    global guilds, raw_settings

    guilds[member.guild]["administration"]["mutes"][member] = {"date": date}
    raw_settings["guilds"][str(member.guild.id)]["administration"]["mutes"][str(member.id)] = {
        "date": date.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_mute(member: discord.Member):
    """
    Removes a muted user

    :param member: Member to reomve
    """
    global guilds, raw_settings

    del guilds[member.guild]["administration"]["mutes"][member]
    del raw_settings["guilds"][str(member.guild.id)]["administration"]["mutes"][str(member.id)]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_jail(member: discord.Member, date: datetime, roles):
    """
    Adds a jailed user

    :param member: Member to add
    :param date: Date to unjail user
    :param roles: Roles that jailed user had
    """
    global guilds, raw_settings

    role_ids = []
    for role in roles:
        role_ids.append(role.id)

    guilds[member.guild]["administration"]["jails"][member] = {"date": date, "roles": roles}
    raw_settings["guilds"][str(member.guild.id)]["administration"]["jails"][str(member.id)] = {
        "date": date.strftime("%Y-%m-%d %H:%M:%S"),
        "roles": role_ids
    }
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_jail(member: discord.Member):
    """
    Removes a jailed user

    :param member: Member to remove
    """
    global guilds, raw_settings

    del guilds[member.guild]["administration"]["jails"][member]
    del raw_settings["guilds"][str(member.guild.id)]["administration"]["jails"][str(member.id)]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_staff_channel(channel: discord.TextChannel):
    """
    Sets the staff channel for a guild

    :param channel: Channel to set to
    """
    global guilds, raw_settings

    guilds[channel.guild]["logging"]["staff"] = channel
    raw_settings["guilds"][str(channel.guild.id)]["logging"]["staff"] = channel.id
    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_staff_channel(guild: discord.Guild):
    """
    Clears the staff channel for the guild

    :param guild: Guild to clear staff channel for
    """
    global guilds, raw_settings

    guilds[guild]["logging"]["staff"] = raw_settings["guilds"][str(guild.id)]["logging"]["staff"] = None
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_close_time():
    """
    Sets the closing time for the bot
    """
    global close_time, raw_settings

    close_time = datetime.now()
    raw_settings["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_close_time():
    """
    Sets the close_time
    """
    global close_time, raw_settings

    close_time = raw_settings["close_time"] = None
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_announcement_channel(channel: discord.TextChannel):
    """
    Adds an announcement channel for a guild

    :param channel: Channel to add
    """
    global guilds, raw_settings

    raw_settings["guilds"][str(channel.guild.id)]["announcement_channels"].append(channel.id)
    guilds[channel.guild]["announcement_channels"].append(channel)
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_announcement_channel(channel: discord.TextChannel):
    """
    Adds an announcement channel for a guild

    :param channel: Channel to add
    """
    global guilds, raw_settings

    raw_settings["guilds"][str(channel.guild.id)]["announcement_channels"].remove(channel.id)
    guilds[channel.guild]["announcement_channels"].remove(channel)
    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_command_channel(channel: discord.TextChannel):
    """
    Adds a command channel for a guild

    :param channel: Channel to add
    """
    global guilds, raw_settings

    raw_settings["guilds"][str(channel.guild.id)]["command_channels"].append(channel.id)
    guilds[channel.guild]["command_channels"].append(channel)
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_command_channel(channel: discord.TextChannel):
    """
    Removes a command channel

    :param channel: Channel to remove
    """
    global guilds, raw_settings

    raw_settings["guilds"][str(channel.guild.id)]["command_channels"].remove(channel.id)
    guilds[channel.guild]["command_channels"].remove(channel)
    save_json(os.path.join("config", "settings.json"), raw_settings)


def save_statuses(statuses):
    """
    Saves member statuses

    :param statuses: Dictionary of statuses to save
    """
    pickle.dump(statuses, open(os.path.join("config", "statuses.p"), "wb+"))


def load_statuses():
    """
    Loads statuses from pickle

    :return: Dictionary of statuses
    """
    try:
        return pickle.load(open(os.path.join("config", "statuses.p"), "rb"))
    except (OSError, IOError) as e:
        return {}


def add_lockout(member: discord.Member):
    """
    Adds a user to lockout list

    :param member: Member to lockout
    """
    global lockouts, raw_settings

    lockouts[member] = member.roles

    role_ids = []
    for role in member.roles:
        role_ids.append(role.id)

    raw_settings["lockouts"][str(member.id)] = role_ids
    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_lockout(member: discord.Member):
    """
    Removes a user from the lockout list

    :param member: Member to lockout
    """
    global lockouts, raw_settings

    del lockouts[member]
    del raw_settings["lockouts"][str(member.id)]
    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_muted_role(role: discord.Role):
    """
    Adds a muted role

    :param role: Role to set to
    """
    global guilds, raw_settings

    guilds[role.guild]["muted_role"] = role
    raw_settings["guilds"][str(role.guild.id)]["muted_role"] = role.id
    save_json(os.path.join("config", "settings.json"), raw_settings)
