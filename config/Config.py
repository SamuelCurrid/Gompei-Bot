from GompeiFunctions import load_json, save_json
from discord.ext import commands
from datetime import timedelta
from datetime import datetime

import collections
import discord
import pickle
import typing
import os

client = None
close_time = None
dm_channel = None
lockouts = {}
main_guild = None
mod_uptime_thread = None
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

    status = raw_settings["status"]
    if status is not None:
        await client.change_presence(activity=discord.Game(name=status))

    for guild in client.guilds:
        if str(guild.id) in raw_settings["guilds"]:
            await update_guild_settings(guild)
        else:
            add_guild(guild)

    if main_guild is not None:
        await update_main_guild_settings()


async def set_main_guild(new_guild: discord.Guild):
    """
    Sets the guild to be used by the bot

    :param new_guild: Guild object
    """
    global main_guild, raw_settings

    main_guild = new_guild
    raw_settings["main_guild"] = main_guild.id

    await update_main_guild_settings()

    save_json(os.path.join("config", "settings.json"), raw_settings)


async def update_main_guild_settings():
    """
    Updates guild settings for the currently selected guild
    """
    global dm_channel, guilds, lockouts, main_guild, mod_uptime_thread

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

    if raw_settings["mod_uptime_thread"] is not None:
        mod_uptime_thread = main_guild.get_thread(raw_settings["mod_uptime_thread"])

        if mod_uptime_thread is None:
            async for thread in guilds[main_guild]["logging"]["mod"].archived_threads:
                if thread.id == raw_settings["mod_uptime_thread"]:
                    mod_uptime_thread = thread
                    break





async def update_guild_settings(guild: discord.Guild):
    """
    Updates guild settings for guilds
    """
    global guilds

    guilds[guild] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "closed": False,
        "opt_in_roles": [],
        "announcement_channels": [],
        "command_channels": [],
        "muted_role": None,
        "reaction_roles": {},
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
        },
        "verifications": {
            "wpi_role": None,
            "wpi": {},
            "member_role": None,
            "message_req": None,
            "time_req": None,
            "member": {}
        }
    }

    # Nitro role
    update_nitro_role(guild)

    # Command Channels
    for channel_id in raw_settings["guilds"][str(guild.id)]["command_channels"]:
        channel = guild.get_channel(channel_id)

        if channel is None:
            raw_settings["guilds"][str(guild.id)]["command_channels"].remove(channel_id)
        else:
            guilds[guild]["command_channels"].append(channel)

    # Access Roles
    for role_id in raw_settings["guilds"][str(guild.id)]["access_roles"]:
        guilds[guild]["access_roles"].append(guild.get_role(role_id))

    # Closed
    guilds[guild]["closed"] = raw_settings["guilds"][str(guild.id)]["closed"]

    # Opt-in Roles
    for role_id in raw_settings["guilds"][str(guild.id)]["opt_in_roles"]:
        guilds[guild]["opt_in_roles"].append(guild.get_role(role_id))

    # Reaction Roles
    for combo_id in raw_settings["guilds"][str(guild.id)]["reaction_roles"]:
        message = await guild.get_channel(int(combo_id[0:18])).fetch_message(int(combo_id[18:]))

        guilds[guild]["reaction_roles"][message] = {
            "emojis": {},
            "exclusive": raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["exclusive"]
        }

        for emote in raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"]:
            # Fake ctx for EmojiConverter
            ctx = collections.namedtuple('Context', 'bot guild', module=commands.context)
            ctx.bot = client
            ctx.guild = guild

            try:
                emoji = await commands.EmojiConverter().convert(ctx, emote)
            except commands.BadArgument:
                emoji = emote

            if isinstance(emoji, str):
                role_id = raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]["role"]
                dm_message = raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][emoji][
                    "message"]
                roles = []
                for required_role_id in \
                        raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][emoji][
                            "reqs"]:
                    role = guild.get_role(required_role_id)

                    if role is None:
                        continue
                    else:
                        roles.append(role)
            else:
                role_id = raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)][
                    "role"]
                dm_message = raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)][
                    "message"]
                roles = []
                for required_role_id in \
                raw_settings["guilds"][str(guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)]["reqs"]:
                    role = guild.get_role(required_role_id)

                    if role is None:
                        continue
                    else:
                        roles.append[role]

            guilds[guild]["reaction_roles"][message]["emojis"][emoji] = {
                "role": guild.get_role(role_id),
                "message": dm_message,
                "reqs": roles
            }

            # If role deleted
            if guilds[guild]["reaction_roles"][message]["emojis"][emoji] is None:
                remove_reaction_role(message, emoji)

    # Logging Channels / Info
    for key in guilds[guild]["logging"]["overwrite_channels"]:
        guilds[guild]["logging"]["overwrite_channels"][key] = \
            guild.get_channel(raw_settings["guilds"][str(guild.id)]["logging"]["overwrite_channels"][key])

    try:
        guilds[guild]["logging"]["last_audit"] = (await guild.audit_logs(limit=1).flatten())[0].id
    except IndexError:
        pass

    guilds[guild]["logging"]["staff"] = guild.get_channel(raw_settings["guilds"][str(guild.id)]["logging"]["staff"])

    # Invites
    for invite in await guild.invites():
        guilds[guild]["logging"]["invites"][invite] = {
            "inviter_id": invite.inviter.id,
            "uses": invite.uses
        }

        if invite.code in raw_settings["guilds"][str(guild.id)]["logging"]["invites"]:
            guilds[guild]["logging"]["invites"][invite]["note"] = \
                raw_settings["guilds"][str(guild.id)]["logging"]["invites"][invite.code]
        else:
            guilds[guild]["logging"]["invites"][invite]["note"] = None

    try:
        vanity_url = await guild.vanity_invite()

        guilds[guild]["logging"]["invites"][vanity_url] = {
            "invite_id": None,
            "uses": invite.uses
        }
    except discord.Forbidden:
        pass

    # Administration
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

    # Verifications
    guilds[guild]["verifications"]["member_role"] = \
        guild.get_role(raw_settings["guilds"][str(guild.id)]["verifications"]["member_role"])
    guilds[guild]["verifications"]["message_req"] = \
        raw_settings["guilds"][str(guild.id)]["verifications"]["message_req"]

    if raw_settings["guilds"][str(guild.id)]["verifications"]["time_req"] is None:
        guilds[guild]["verifications"]["time_req"] = None
    else:
        guilds[guild]["verifications"]["time_req"] = timedelta(
            seconds=raw_settings["guilds"][str(guild.id)]["verifications"]["time_req"]
        )

    for user_id in raw_settings["guilds"][str(guild.id)]["verifications"]["member"]:
        member = guild.get_member(int(user_id))
        if member is None:
            continue

        if raw_settings["guilds"][str(guild.id)]["verifications"]["member"][str(member.id)]["verified"] is None:
            guilds[guild]["verifications"]["member"][member] = {
                "datetime": None,
                "message_count": None,
                "verified": None
            }
        else:
            guilds[guild]["verifications"]["member"][member] = {
                "datetime": datetime.strptime(
                    raw_settings["guilds"][str(guild.id)]["verifications"]["member"][user_id]["datetime"],
                    "%Y-%m-%d %H:%M:%S"
                ),
                "message_count":
                    raw_settings["guilds"][str(guild.id)]["verifications"]["member"][user_id]["message_count"],
                "verified": raw_settings["guilds"][str(guild.id)]["verifications"]["member"][user_id]["verified"]
            }

    guilds[guild]["verifications"]["wpi_role"] = \
        guild.get_role(raw_settings["guilds"][str(guild.id)]["verifications"]["wpi_role"])

    for token in raw_settings["guilds"][str(guild.id)]["verifications"]["wpi"]:
        guilds[guild]["verifications"]["wpi"][token] = \
            raw_settings["guilds"][str(guild.id)]["verifications"]["wpi"][token]


def add_guild(guild: discord.Guild):
    global guilds, raw_settings

    guilds[guild] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "closed": False,
        "opt_in_roles": [],
        "command_channels": [],
        "muted_role": None,
        "reaction_roles": {},
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
        },
        "verifications": {
            "wpi": {},
            "wpi_role": None,
            "member_role": None,
            "message_req": None,
            "time_req": None,
            "member": {}
        }
    }

    raw_settings["guilds"][str(guild.id)] = {
        "nitro_role": None,
        "prefix": None,
        "access_roles": [],
        "closed": False,
        "opt_in_roles": [],
        "command_channels": [],
        "muted_role": None,
        "reaction_roles": {},
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
        },
        "verifications": {
            "wpi": {},
            "wpi_role": None,
            "member_role": None,
            "message_req": None,
            "time_req": None,
            "member": {}
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


def set_logging_channel(logging_type: str, channel: discord.TextChannel):
    """
    Sets the logging channel for the bot

    :param logging_type: Type of logging channel to set
    :param channel: Channel to use for logging
    """
    global guilds, raw_settings

    guilds[channel.guild]["logging"]["overwrite_channels"][logging_type] = channel
    raw_settings["guilds"][str(channel.guild.id)]["logging"]["overwrite_channels"][logging_type] = channel.id
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

    guilds[invite.guild]["logging"]["invites"][invite] = {
        "inviter_id": invite.inviter.id,
        "uses": invite.uses,
        "note": None
    }


def remove_invite(invite: discord.Invite):
    """
    Removes an invite

    :param invite: Invite code
    """
    global guilds, raw_settings

    del guilds[invite.guild]["logging"]["invites"][invite]


def update_invite_uses(invite: discord.Invite):
    """
    Updates the amount of times an invite has been used

    :param invite: invite code
    """
    global guilds, raw_settings

    guilds[invite.guild]["logging"]["invites"][invite]["uses"] = invite.uses


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


def add_reaction_role(message: discord.Message, emoji: typing.Union[discord.Emoji, str], role: discord.Role):
    """
    Adds a reaction role to a message

    :param message: Message to add reaction role to
    :param emoji: Emoji to react with
    :param role: Role to give on react
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)

    # If reacts already exist on the message
    if message in guilds[message.guild]["reaction_roles"]:
        guilds[message.guild]["reaction_roles"][message]["emojis"][emoji] = {
            "role": role,
            "message": None,
            "reqs": []
        }

        if isinstance(emoji, str):
            raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji] = {
                "role": role.id,
                "message": None,
                "reqs": []
            }
        else:
            raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)] = {
                "role": role.id,
                "message": None,
                "reqs": []
            }

    else:
        guilds[message.guild]["reaction_roles"][message] = {
            "emojis": {
                emoji: {
                    "role": role,
                    "message": None,
                    "reqs": []
                }
            },
            "exclusive": False
        }

        if isinstance(emoji, str):
            raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id] = {
                "emojis": {
                    emoji: {
                        "role": role.id,
                        "message": None,
                        "reqs": []
                    }
                },
                "exclusive": False
            }
        else:
            raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id] = {
                "emojis": {
                    str(emoji.id): {
                        "role": role.id,
                        "message": None,
                        "reqs": []
                    }
                },
                "exclusive": False
            }

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_reaction_role(message: discord.Message, emoji: typing.Union[discord.Emoji, str]):
    """
    Removes a reaction role from a message
    
    :param message: Message to remove reaction role from 
    :param emoji: Emoji to remove
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)

    del guilds[message.guild]["reaction_roles"][message]["emojis"][emoji]

    if isinstance(emoji, str):
        del raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]
    else:
        del raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)]

    if len(guilds[message.guild]["reaction_roles"][message]["emojis"]) == 0:
        del guilds[message.guild]["reaction_roles"][message]
        del raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_reaction_message_exclusivity(message: discord.Message, exclusive: bool):
    """
    Makes reaction roles on a message exclusive/inclusive

    :param message: Message to set exclusive/inclusive
    :param exclusive: bool for whether the reaction role is exclusive
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)
    guilds[message.guild]["reaction_roles"][message]["exclusive"] = True
    raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["exclusive"] = exclusive

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_reaction_role_message(message: discord.Message, emoji: typing.Union[discord.Emoji, str], msg: str):
    """
    Sets the message to be sent to a user for a reaction role

    :param message: Message that has the reaction role
    :param emoji: Emoji for the reaction role
    :param msg: String to send to the member who reacts
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)
    guilds[message.guild]["reaction_roles"][message]["emojis"][emoji]["message"] = msg
    if isinstance(emoji, str):
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]["message"] = msg
    else:
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)]["message"] \
            = msg

    save_json(os.path.join("config", "settings.json"), raw_settings)


def clear_reaction_role_message(message: discord.Message, emoji: typing.Union[discord.Emoji, str]):
    """
    Removes the message for a reaction role

    :param message: Message that has the reaction role
    :param emoji: Emoji for the reaction role
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)
    guilds[message.guild]["reaction_roles"][message]["emojis"][emoji]["message"] = None
    if isinstance(emoji, str):
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]["message"] = None
    else:
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)]["message"] \
            = None

    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_reaction_role_requirement(message: discord.Message, emoji: typing.Union[discord.Emoji, str],
                                  role: discord.Role):
    """
    Adds a role requirement for a reaction role

    :param message: Message that has the reaction role
    :param emoji: Emoji for the reaction role
    :param role: Role to set as a requirement
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)
    guilds[message.guild]["reaction_roles"][message]["emojis"][emoji]["reqs"].append(role)
    if isinstance(emoji, str):
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]["reqs"].append(
            role.id
        )
    else:
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)][
            "reqs"].append(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_reaction_role_requirement(message: discord.Message, emoji: typing.Union[discord.Emoji, str],
                                     role: discord.Role):
    """
    Removes a role requirement for a reaction role

    :param message: Message that has the reaction role
    :param emoji: Emoji for the reaction role
    :param role: Role to remove as a requirement
    """
    global guilds, raw_settings

    combo_id = str(message.channel.id) + str(message.id)
    guilds[message.guild]["reaction_roles"][message]["emojis"][emoji]["reqs"].append(role)
    if isinstance(emoji, str):
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][emoji]["reqs"].remove(
            role.id)
    else:
        raw_settings["guilds"][str(message.guild.id)]["reaction_roles"][combo_id]["emojis"][str(emoji.id)][
            "reqs"].remove(role.id)

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_guild_closed(guild: discord.Guild, closed: bool):
    """
    Sets a guild to be closed or not

    :param guild: Guild to set
    :param closed: Whether the guild is closed
    """
    global guilds, raw_settings

    guilds[guild]["closed"] = closed
    raw_settings["guilds"][str(guild.id)]["closed"] = closed

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_invite_note(invite: discord.Invite, note: str):
    """
    Adds a note to an invite

    :param invite: Invite to add note to
    :param note: Note for the invite
    """
    global guilds, raw_settings

    guilds[invite.guild]["logging"]["invites"][invite]["note"] = note
    raw_settings["guilds"][str(invite.guild.id)]["logging"]["invites"][invite.code] = note

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_invite_note(invite: discord.Invite):
    """
    Removes an note for an invite

    :param invite: Invite to remove note for
    """
    global guilds, raw_settings

    del guilds[invite.guild]["logging"]["invites"][invite]["note"]
    del raw_settings["guilds"][str(invite.guild.id)]["logging"]["invites"][invite.code]

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_member_role(role: discord.Role):
    """
    Sets the verification role for members

    :param role: Role to set to
    """
    global guilds, raw_settings

    guilds[role.guild]["verifications"]["member_role"] = role
    raw_settings["guilds"][str(role.guild.id)]["verifications"]["member_role"] = role.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_member_message_req(guild: discord.Guild, number: int):
    """
    Sets the amount of messages required to become verified

    :param guild: Guild to set the requirement for
    :param number: Number of messages required
    """
    global guilds, raw_settings

    guilds[guild]["verifications"]["message_req"] = number
    raw_settings["guilds"][str(guild.id)]["verifications"]["message_req"] = number

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_member_time_req(guild: discord.Guild, time: timedelta):
    """
    Sets the amount of time that needs to pass after the first message is sent in order to get verified

    :param guild: Guild to set the requirement for
    :param time: Number of messages required
    """
    global guilds, raw_settings

    guilds[guild]["verifications"]["time_req"] = time
    raw_settings["guilds"][str(guild.id)]["verifications"]["time_req"] = int(time.total_seconds())

    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_member(member: discord.Member):
    """
    Adds a member to the member list

    :param member: Member to add
    """
    global guilds, raw_settings

    guilds[member.guild]["verifications"]["member"][member] = {
        "datetime": datetime.now(),
        "message_count": 1,
        "verified": False
    }
    raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)] = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message_count": 1,
        "verified": False
    }

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_member(member: discord.Member):
    """
    Removes a member from the member list

    :param member: Member to remove
    """
    global guilds, raw_settings

    del guilds[member.guild]["verifications"]["member"][member]
    del raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)]

    save_json(os.path.join("config", "settings.json"), raw_settings)


def add_message(member: discord.Member):
    """
    Adds a message to a member in the list

    :param member: Member to add message to
    """
    global guilds, raw_settings

    guilds[member.guild]["verifications"]["member"][member]["message_count"] += 1
    raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)]["message_count"] += 1

    save_json(os.path.join("config", "settings.json"), raw_settings)


def remove_message(member: discord.Member):
    """
    Adds a message to a member in the list

    :param member: Member to add message to
    """
    global guilds, raw_settings

    guilds[member.guild]["verifications"]["member"][member]["message_count"] -= 1
    raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)]["message_count"] -= 1

    save_json(os.path.join("config", "settings.json"), raw_settings)


def verify_member(member: discord.Member):
    """
    Verifies a member in the member list

    :param member: Member to verify
    """
    global guilds, raw_settings

    guilds[member.guild]["verifications"]["member"][member]["verified"] = True
    raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)]["verified"] = True

    save_json(os.path.join("config", "settings.json"), raw_settings)


def unverify_member(member: discord.Member):
    """
    Unverifies a member in the member list

    :param member:
    """
    global guilds, raw_settings

    del guilds[member.guild]["verifications"]["member"][member]
    del raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)]

    save_json(os.path.join("config", "settings.json"), raw_settings)


def disable_member_verification(member: discord.Member):
    """
    Disables member verification

    :param member:
    """
    global guilds, raw_settings

    guilds[member.guild]["verifications"]["member"][member] = {
        "datetime": None,
        "message_count": 0,
        "verified": None
    }
    raw_settings["guilds"][str(member.guild.id)]["verifications"]["member"][str(member.id)] = {
        "datetime": None,
        "message_count": 0,
        "verified": None
    }

    save_json(os.path.join("config", "settings.json"), raw_settings)


def set_wpi_member_role(role: discord.Role):
    """
    Sets the WPI verification role

    :param role: Role to set
    """
    global guilds, raw_settings

    guilds[role.guild]["verifications"]["wpi_role"] = role
    raw_settings["guilds"][str(role.guild.id)]["verifications"]["wpi_role"] = role.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


def update_wpi_verifications():
    """
    Checks the verification list and returns new WPI verified IDs

    :return: List of new IDs
    """
    global guilds, raw_settings

    # Open the verification file and read the user IDs. Compare to the ones stored here.
    verifications = load_json("/var/www/WPI-Discord-Flask/verifications.json")

    new_users = []
    for token in verifications:
        if token not in guilds[main_guild]["verifications"]["wpi"]:
            guilds[main_guild]["verifications"]["wpi"][token] = verifications[token]
            raw_settings["guilds"][str(main_guild.id)]["verifications"]["wpi"][token] = verifications[token]
            new_users.append(verifications[token])

    if len(new_users) > 0:
        save_json(os.path.join("config", "settings.json"), raw_settings)

    return new_users


def load_highlights():
    """
    Loads highlights from pickle

    :return: Highlights dictionary
    """
    try:
        return pickle.load(open(os.path.join("config", "highlights.p"), "rb"))
    except (OSError, IOError) as e:
        return {}


def save_highlights(highlights):
    """
    Saves highlight to a pickle
    """
    pickle.dump(highlights, open(os.path.join("config", "highlights.p"), "wb+"))

def set_mod_uptime_thread(thread: discord.Thread):
    """
    Saves the mod uptime thread

    :param thread: Thread to save
    """
    global mod_uptime_thread, raw_settings

    mod_uptime_thread = thread
    raw_settings["mod_uptime_thread"] = thread.id

    save_json(os.path.join("config", "settings.json"), raw_settings)


