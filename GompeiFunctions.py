from dateutil import relativedelta

import discord
import json


def make_ordinal(number):
    """
    Coverts an integer to an ordinal string

    :param number: integer to convert
    :return: ordinal string
    """
    number = int(number)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(number % 10, 4)]
    if 11 <= (number % 100) <= 13:
        suffix = 'th'
    return str(number) + suffix


def time_delta_string(before, after):
    """
    Returns a string with three most significant time deltas between date1 and date2

    :param before: datetime 1
    :param after: datetime 2
    :return: string
    """
    if after == before:
        return "0 seconds"

    delta = relativedelta.relativedelta(after, before)

    if delta.years > 0:
        if delta.years == 1:
            output = str(delta.years) + " year, "
        else:
            output = str(delta.years) + " years, "
        if delta.months == 1:
            output += str(delta.months) + " month, "
        else:
            output += str(delta.months) + " months, "

        if delta.days == 1:
            output += "and " + str(delta.days) + " day"
        else:
            output += "and " + str(delta.days) + " days"

        return output

    elif delta.months > 0:
        if delta.months == 1:
            output = str(delta.months) + " month, "
        else:
            output = str(delta.months) + " months, "
        if delta.days == 1:
            output += str(delta.days) + " day, "
        else:
            output += str(delta.days) + " days, "
        if delta.hours == 1:
            output += "and " + str(delta.hours) + " hour"
        else:
            output += "and " + str(delta.hours) + " hours"

        return output

    elif delta.days > 0:
        if delta.days == 1:
            output = str(delta.days) + " day, "
        else:
            output = str(delta.days) + " days, "
        if delta.hours == 1:
            output += str(delta.hours) + " hour, "
        else:
            output += str(delta.hours) + " hours, "
        if delta.minutes == 1:
            output += "and " + str(delta.minutes) + " minute"
        else:
            output += "and " + str(delta.minutes) + " minutes"

        return output

    elif delta.hours > 0:
        if delta.hours == 1:
            output = str(delta.hours) + " hour, "
        else:
            output = str(delta.hours) + " hours, "
        if delta.minutes == 1:
            output += str(delta.minutes) + " minute, "
        else:
            output += str(delta.minutes) + " minutes, "
        if delta.seconds == 1:
            output += "and " + str(delta.seconds) + " second"
        else:
            output += "and " + str(delta.seconds) + " seconds"

        return output

    elif delta.minutes > 0:
        if delta.minutes == 1:
            output = str(delta.minutes) + " minute "
        else:
            output = str(delta.minutes) + " minutes "
        if delta.seconds == 1:
            output += "and " + str(delta.seconds) + " second"
        else:
            output += "and " + str(delta.seconds) + " seconds"

        return output

    elif delta.seconds > 0:
        if delta.seconds == 1:
            return str(delta.seconds) + " second"
        else:
            return str(delta.seconds) + " seconds"

    return "!!DATETIME ERROR!!"


def load_json(file_path):
    """
    Loads json from a file

    :param file_path: the path to the file
    :return: dictionary
    """
    try:
        with open(file_path, "r+") as file:
            return json.loads(file.read())
    except (OSError, IOError):
        with open(file_path, "r+") as file:
            file.truncate(0)
            file.seek(0)
            json.dump("{}", file, indent=4)
            return {}


def save_json(file_path, data):
    """
    Saves a dictionary to a json file

    :param file_path: file to save to
    :param data: dictionary to save
    """
    with open(file_path, "r+") as file:
        file.truncate(0)
        file.seek(0)
        json.dump(data, file, indent=4)


def parse_id(arg):
    """
    Parses an ID from a discord @

    :param arg: @ or ID passed
    :return: ID
    """
    if "<" in arg:
        for i, c in enumerate(arg):
            if c.isdigit():
                return int(arg[i:-1])
    else:
        return int(arg)


async def yes_no_helper(bot, ctx):
    """
    Waits for a yes or no response for the user

    :param bot: Bot that is processing the message
    :param ctx: Context object for the message
    :return: True if yes, False if no
    """
    while True:
        def check_author(m):
            return m.author.id == ctx.author.id

        response = await bot.wait_for('message', check=check_author)

        if response.content.lower() == "y" or response.content.lower() == "yes":
            return True
        elif response.content.lower() == "n" or response.content.lower() == "no":
            return False
        else:
            await ctx.send("Did not recognize your response. Make sure it is a yes or a no.")
