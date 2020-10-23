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
