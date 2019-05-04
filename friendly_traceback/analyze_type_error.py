"""analyze_type_error.py

Collection of functions useful in parsing TypeError messages.
"""

import re

from .my_gettext import current_lang


possible_causes = []


def add_cause(func):
    """A simple decorator that adds a given cause to the list
       of probable causes."""
    possible_causes.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


def convert_message(message):
    for cause in possible_causes:
        result = cause(message)
        if result is not None:
            return result
    return None


def convert_type(short_form):
    _ = current_lang.lang
    if short_form == "dict":
        return _("a dictionary ('dict')")
    elif short_form == "int":
        return _("an integer ('int')")
    elif short_form == "list":
        return _("a list")
    elif short_form == "set":
        return _("a set")
    elif short_form == "str":
        return _("a string ('str')")
    elif short_form == "tuple":
        return _("a tuple")
    else:
        return short_form


# example: can only concatenate str (not "int") to str
can_only_concatenate_pattern = re.compile(
    r"can only concatenate (\w+) \(not [\'\"](\w+)[\'\"]\) to (\w+)"
)


@add_cause
def parse_can_only_concatenate(text):
    _ = current_lang.lang
    match = re.search(can_only_concatenate_pattern, text)
    if match is not None:
        cause = _(
            "        You tried to concatenate (add) two different types of objects:\n"
            "        {first} and {second}\n"
        ).format(
            first=convert_type(match.group(1)), second=convert_type(match.group(2))
        )
        return cause
    else:
        return None
