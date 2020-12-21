"""value_error.py

Collection of functions useful in parsing ValueError messages and
providing a more detailed explanation.
"""

import re

from ..my_gettext import current_lang
from .. import info_variables

convert_type = info_variables.convert_type
MESSAGES_PARSERS = []


def add_message_parser(func):
    """A simple decorator that adds a function to parse a specific message
    to the list of known parsers."""
    MESSAGES_PARSERS.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


def get_cause(value, frame, tb_data):
    _ = current_lang.translate
    unknown = _(
        "I do not recognize this case. Please report it to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )
    message = str(value)
    for parser in MESSAGES_PARSERS:
        cause, hint = parser(message, frame, tb_data)
        if cause is not None:
            return cause, hint
    return unknown, None


def _unpacking():
    _ = current_lang.translate
    return _(
        "Unpacking is a convenient way to assign a name,\n"
        "to each item of an iterable.\n"
    )


@add_message_parser
def too_many_values_to_unpack(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"too many values to unpack \(expected (\d+)\)")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    nb_names = match.group(1)

    if tb_data.bad_line.count("=") != 1:
        cause = _unpacking() + _(
            "In this instance, you have fewer names (`{nb_names}`)\n"
            "than the length of the iterable.\n"
        ).format(nb_names=nb_names)
        return cause, hint

    lhs, rhs = tb_data.bad_line.split("=")
    try:
        rhs = eval(rhs, frame.f_globals, frame.f_locals)
        length = len(rhs)
    except Exception:
        cause = _unpacking() + _(
            "In this instance, you have fewer names (`{nb_names}`)\n"
            "than the length of the iterable.\n"
        ).format(nb_names=nb_names)
        return cause, hint

    if isinstance(rhs, dict):
        iterable = "dict"
    elif isinstance(rhs, list):
        iterable = "list"
    elif isinstance(rhs, set):
        iterable = "set"
    elif isinstance(rhs, str):
        iterable = "str"
    elif isinstance(rhs, tuple):
        iterable = "tuple"
    else:
        iterable = "an_unknown_type"

    cause = _unpacking() + _(
        "In this instance, you have fewer names (`{nb_names}`)\n"
        "than the length of the iterable, {iter_type} of length `{length}`.\n"
    ).format(nb_names=nb_names, iter_type=convert_type(iterable), length=length)
    return cause, hint
