"""value_error.py

Collection of functions useful in parsing ValueError messages and
providing a more detailed explanation.
"""

import inspect
import re

from ..my_gettext import current_lang, no_information, internal_error
from .. import info_variables
from .. import debug_helper
from .. import token_utils
from .. import utils

convert_type = info_variables.convert_type
MESSAGES_PARSERS = []


def add_message_parser(func):
    """A simple decorator that adds a function to parse a specific message
    to the list of known parsers."""
    MESSAGES_PARSERS.append(func)


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:  # pragma: no cover
        debug_helper.log_error(e)
        return {"cause": internal_error(), "suggest": internal_error()}


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    message = str(value)
    for parser in MESSAGES_PARSERS:
        cause = parser(message, frame, tb_data)
        if cause:
            return cause
    cause = unrecognized_message(value, frame, tb_data)
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
        # As a ValueError exception has been raised, Python has already evaluated
        # all the relevant code parts. Thus, using eval should be completely safe.
        obj = utils.eval_expr(code, frame)
        # obj = eval(code, frame.f_globals, frame.f_locals)
    except Exception:  # noqa
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


# TODO: complete the work below; note noqa to be removed


@add_message_parser
def invalid_literal_for_int(message, *_args):
    _ = current_lang.translate
    pattern = re.compile(r"invalid literal for int\(\) with base (\d+): '(.*)'")
    match = re.search(pattern, message)
    if match is None:
        return {}
    base, value = int(match.group(1)), match.group(2).strip()
    if base == 10:
        try:
            _value = float(value)  # noqa
            return _convert_to_float(value)
        except ValueError:
            pass

    return {}


def _convert_to_float(value):
    _ = current_lang.translate

    hint = _("You need to convert to a float first.\n")
    cause = _(
        "The string `'{value}'` needs to be first converted using `float()`\n"
        "before the result can be converted into an integer using `int()`.\n"
    ).format(value=value)
    return {"cause": cause, "suggest": hint}


@add_message_parser
def date_month_must_be_between_1_and_12(message, *_args):
    _ = current_lang.translate

    if message != "month must be in 1..12":
        return {}

    hint = _("Did you specify an invalid month?\n")
    cause = _(
        "I am guessing that you specify an invalid value for a month\n"
        "in a `date` object. Valid values are integers, from 1 to 12.\n"
    )
    return {"cause": cause, "suggest": hint}


def unrecognized_message(_value, frame, tb_data):
    """This attempts to provide some help when a message is not recognized."""
    _ = current_lang.translate
    bad_line = tb_data.bad_line.strip()
    if bad_line.startswith("raise ") or bad_line.startswith("raise\t"):
        try:
            name = inspect.getframeinfo(frame).function
            fn_obj = frame.f_globals[name]
        except Exception:
            return {}
    else:
        all_objects = info_variables.get_all_objects(bad_line, frame)["name, obj"]
        callables = []
        for name, obj in all_objects:
            if callable(obj):
                callables.append((name, obj))
        if not callables:
            return {}

        tokens = token_utils.get_significant_tokens(tb_data.bad_line)
        name, fn_obj = callables[0]
        if name != tokens[0]:
            return {}

    cause = _(
        "I do not recognize this error message.\n"
        "I am guessing that the problem is with the function `{name}`.\n"
    ).format(name=name)

    if hasattr(fn_obj, "__doc__") and fn_obj.__doc__ is not None:
        cause += _("Its docstring is:\n\n`'''{docstring}'''`\n").format(
            docstring=fn_obj.__doc__
        )
    else:
        cause += _("I have no more information.\n")
    return {"cause": cause}
