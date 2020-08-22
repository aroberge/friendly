"""analyze_type_error.py

Collection of functions useful in parsing TypeError messages and
providing a more detailed explanation.
"""

import re

from .my_gettext import current_lang


MESSAGES_PARSERS = []


def add_message_parser(func):
    """A simple decorator that adds a function to parse a specific message
       to the list of known parsers."""
    MESSAGES_PARSERS.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


def convert_message(message):
    _ = current_lang.translate
    for parser in MESSAGES_PARSERS:
        cause = parser(message)
        if cause is not None:
            return cause
    return _(
        "I do not recognize this case. Please report it to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def convert_type(short_form):
    _ = current_lang.translate
    if short_form == "complex":
        return _("a complex number")
    elif short_form == "dict":
        return _("a dictionary (`dict`)")
    elif short_form == "float":
        return _("a number (`float`)")
    elif short_form == "int":
        return _("an integer (`int`)")
    elif short_form == "list":
        return _("a `list`")
    elif short_form == "NoneType":
        return _("a variable equal to None (`NoneType`)")
    elif short_form == "set":
        return _("a `set`")
    elif short_form == "str":
        return _("a string (`str`)")
    elif short_form == "tuple":
        return _("a `tuple`")
    else:
        return short_form


@add_message_parser
def parse_can_only_concatenate(message):
    _ = current_lang.translate
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(
        r"can only concatenate (\w+) \(not [\'\"](\w+)[\'\"]\) to (\w+)"
    )
    match = re.search(pattern, message)
    cause = None
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}\n"
        ).format(
            first=convert_type(match.group(1)), second=convert_type(match.group(2))
        )
    return cause


@add_message_parser
def parse_must_be_str(message):
    _ = current_lang.translate
    # python 3.6 version: must be str, not int
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(r"must be str, not (\w+)")
    match = re.search(pattern, message)
    cause = None
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}\n"
        ).format(first=convert_type("str"), second=convert_type(match.group(1)))
    return cause


@add_message_parser
def parse_unsupported_operand_type(message):
    _ = current_lang.translate
    # example: unsupported operand type(s) for +: 'int' and 'str'
    pattern = re.compile(
        r"unsupported operand type\(s\) for (.+): [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"
    )
    match = re.search(pattern, message)
    cause = None
    if match is not None:
        operator = match.group(1)
        if operator in ["+", "+="]:
            cause = _(
                "You tried to add two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["-", "-="]:
            cause = _(
                "You tried to subtract two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["*", "*="]:
            cause = _(
                "You tried to multiply two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["/", "//", "/=", "//="]:
            cause = _(
                "You tried to divide two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["&", "|", "^", "&=", "|", "^="]:
            cause = _(
                "You tried to perform the bitwise operation {operator}\n"
                "on two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                operator=operator,
                first=convert_type(match.group(2)),
                second=convert_type(match.group(3)),
            )
        elif operator in [">>", "<<", ">>=", "<<="]:
            cause = _(
                "You tried to perform the bit shifting operation {operator}\n"
                "on two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                operator=operator,
                first=convert_type(match.group(2)),
                second=convert_type(match.group(3)),
            )
        elif operator == "** or pow()":
            cause = _(
                "You tried to exponentiate (raise to a power)\n"
                "using two incompatible types of objects:\n"
                "{first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["@", "@="]:
            cause = _(
                "You tried to use the operator {operator}\n"
                "using two incompatible types of objects:\n"
                "{first} and {second}.\n"
                "This operator is normally used only\n"
                "for multiplication of matrices.\n"
            ).format(
                operator=operator,
                first=convert_type(match.group(2)),
                second=convert_type(match.group(3)),
            )
    return cause


@add_message_parser
def parse_order_comparison(message):
    _ = current_lang.translate
    # example: '<' not supported between instances of 'int' and 'str'
    pattern = re.compile(
        r"[\'\"](.+)[\'\"] not supported between instances of [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"  # noqa
    )
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to do an order comparison ({operator})\n"
            "between two incompatible types of objects:\n"
            "{first} and {second}\n"
        ).format(
            operator=match.group(1),
            first=convert_type(match.group(2)),
            second=convert_type(match.group(3)),
        )
        return cause
    else:
        return


@add_message_parser
def bad_operand_type_for_unary(message):
    _ = current_lang.translate

    # example: bad operand type for unary +: 'str'
    pattern = re.compile(r"bad operand type for unary (.+): [\'\"](\w+)[\'\"]")
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to use the unary operator '{operator}'\n"
            "with the following type of object: {obj}.\n"
            "This operation is not defined for this type of object.\n"
        ).format(operator=match.group(1), obj=convert_type(match.group(2)))
        return cause
    else:
        return


@add_message_parser
def does_not_support_item_asssignment(message):
    _ = current_lang.translate
    # example: 'tuple' object does not support item assignment
    pattern = re.compile(r"[\'\"](\w+)[\'\"] object does not support item assignment")
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "In Python, some objects are known as immutable:\n"
            "once defined, their value cannot be changed.\n"
            "You tried change part of such an immutable object: {obj},\n"
            "most likely by using an indexing operation.\n"
        ).format(obj=convert_type(match.group(1)))
        return cause
    else:
        return


@add_message_parser
def exception_derived_from_BaseException(message):
    _ = current_lang.translate
    if "exceptions must derive from BaseException" in message:
        return _("In Python 3, exceptions must be derived from BaseException.\n")


@add_message_parser
def incorrect_nb_positional_arguments(message):
    _ = current_lang.translate
    # example: my_function() takes 0 positional arguments but 1 was given
    pattern = re.compile(r"(.*) takes (\d+) positional arguments but (\d+) was given")
    match = re.search(pattern, message)

    if match is not None:
        cause = _(
            "You apparently have called the function '{fn_name}' with\n"
            "{nb_given} positional argument while it requires {nb_required}\n"
            "such positional arguments.\n"
        ).format(
            fn_name=match.group(1), nb_given=match.group(3), nb_required=match.group(2)
        )
        return cause
    else:
        return


@add_message_parser
def missing_positional_arguments(message):
    _ = current_lang.translate
    # example: my_function() missing 1 required positional argument
    pattern = re.compile(r"(.*) missing (\d+) required positional argument")
    match = re.search(pattern, message)

    if match is not None:
        cause = _(
            "You apparently have called the function '{fn_name}' with\n"
            "fewer positional arguments than it requires ({nb_required} missing).\n"
        ).format(fn_name=match.group(1), nb_required=match.group(2))
        return cause
    else:
        return


@add_message_parser
def x_is_not_callable(message):
    _ = current_lang.translate
    pattern = re.compile(r"'(.*)' object is not callable")
    match = re.search(pattern, message)
    if match is not None:
        obj = match.group(1)
        if obj == "tuple":
            perhaps = _("Perhaps you had a missing comma between two tuples.\n")
        else:
            perhaps = _("Perhaps you had a missing comma before the tuple.\n")
        return (
            _(
                "I suspect that you had an object of this type, {obj},\n"
                "followed by what looked like a tuple, '(...)',\n"
                "which Python took as an indication of a function call.\n"
            ).format(obj=convert_type(obj))
            + perhaps
        )
    else:
        return
