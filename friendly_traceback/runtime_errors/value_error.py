"""value_error.py

Collection of functions useful in parsing ValueError messages and
providing a more detailed explanation.
"""

import re

from ..my_gettext import current_lang, no_information, internal_error
from .. import info_variables
from .. import debug_helper

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
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:
        debug_helper.log_error(e)
        return {"cause": internal_error(), "suggest": internal_error()}


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    message = str(value)
    for parser in MESSAGES_PARSERS:
        cause = parser(message, frame, tb_data)
        if cause:
            return cause
    return {"cause": no_information()}


def _unpacking():
    _ = current_lang.translate
    return _(
        "Unpacking is a convenient way to assign a name,\n"
        "to each item of an iterable.\n"
    )


def get_iterable(code, frame):
    """gets an iterable object and its type as a string."""
    try:
        obj = eval(code, frame.f_globals, frame.f_locals)
    except Exception:
        return None, None

    if isinstance(obj, dict):
        iterable = "dict"
    elif isinstance(obj, list):
        iterable = "list"
    elif isinstance(obj, set):
        iterable = "set"
    elif isinstance(obj, str):
        iterable = "str"
    elif isinstance(obj, tuple):
        iterable = "tuple"
    else:
        iterable = None
    return obj, iterable


@add_message_parser
def not_enough_values_to_unpack(message, frame, tb_data):
    _ = current_lang.translate
    pattern1 = re.compile(r"not enough values to unpack \(expected (\d+), got (\d+)\)")
    match1 = re.search(pattern1, message)
    pattern2 = re.compile(
        r"not enough values to unpack \(expected at least (\d+), got (\d+)\)"
    )
    match2 = re.search(pattern2, message)
    if match1 is None and match2 is None:
        return {}

    match = match1 if match2 is None else match2

    nb_names = match.group(1)
    length = match.group(2)

    if tb_data.bad_line.count("=") != 1:
        cause = _unpacking() + _(
            "In this instance, there are more names ({nb_names})\n"
            "than {length}, the length of the iterable.\n"
        ).format(nb_names=nb_names, length=length)
        return {"cause": cause}

    _lhs, rhs = tb_data.bad_line.split("=")
    obj, iterable = get_iterable(rhs, frame)
    if obj is None or iterable is None:
        cause = _unpacking() + _(
            "In this instance, there are more names ({nb_names})\n"
            "than {length}, the length of the iterable.\n"
        ).format(nb_names=nb_names, length=length)
        return {"cause": cause}

    cause = _unpacking() + _(
        "In this instance, there are more names ({nb_names})\n"
        "than the length of the iterable, {iter_type} of length {length}.\n"
    ).format(nb_names=nb_names, iter_type=convert_type(iterable), length=length)
    return {"cause": cause}


@add_message_parser
def too_many_values_to_unpack(message, frame, tb_data):
    _ = current_lang.translate
    pattern = re.compile(r"too many values to unpack \(expected (\d+)\)")
    match = re.search(pattern, message)
    if match is None:
        return {}

    nb_names = match.group(1)

    if tb_data.bad_line.count("=") != 1:
        cause = _unpacking() + _(
            "In this instance, there are fewer names ({nb_names})\n"
            "than the length of the iterable.\n"
        ).format(nb_names=nb_names)
        return {"cause": cause}

    _lhs, rhs = tb_data.bad_line.split("=")

    obj, iterable = get_iterable(rhs, frame)
    if obj is None or iterable is None or not hasattr(obj, "__len__"):
        cause = _unpacking() + _(
            "In this instance, there are fewer names ({nb_names})\n"
            "than the length of the iterable.\n"
        ).format(nb_names=nb_names)
        return {"cause": cause}

    cause = _unpacking() + _(
        "In this instance, there are fewer names ({nb_names})\n"
        "than the length of the iterable, {iter_type} of length {length}.\n"
    ).format(nb_names=nb_names, iter_type=convert_type(iterable), length=len(obj))
    return {"cause": cause}
