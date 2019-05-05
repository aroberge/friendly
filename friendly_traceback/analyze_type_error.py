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
    _ = current_lang.lang
    for cause in possible_causes:
        result = cause(message)
        if result is not None:
            return result
    return _(
        "        I do not recognize this case. Please report it to\n"
        "        https://github.com/aroberge/friendly-traceback/issues\n"
    )


def convert_type(short_form):
    _ = current_lang.lang
    if short_form == "complex":
        return _("a complex number")
    elif short_form == "dict":
        return _("a dictionary ('dict')")
    elif short_form == "float":
        return _("a number ('float')")
    elif short_form == "int":
        return _("an integer ('int')")
    elif short_form == "list":
        return _("a list")
    elif short_form == "NoneType":
        return _("a variable equal to None ('NoneType')")
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


# example: unsupported operand type(s) for +: 'int' and 'str'
unsupported_operand_type_pattern = re.compile(
    r"unsupported operand type\(s\) for (.+): [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"
)


@add_cause
def parse_unsupported_operand_type(text):
    _ = current_lang.lang
    match = re.search(unsupported_operand_type_pattern, text)
    cause = None
    if match is not None:
        operator = match.group(1)
        if operator in ["+", "+="]:
            cause = _(
                "        You tried to add two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["-", "-="]:
            cause = _(
                "        You tried to subtract two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["*", "*="]:
            cause = _(
                "        You tried to multiply two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["/", "//", "/=", "//="]:
            cause = _(
                "        You tried to divide two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
        elif operator in ["&", "|", "^"]:
            cause = _(
                "        You tried to perform the bitwise operation {operator}\n"
                "        on two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                operator=operator,
                first=convert_type(match.group(2)),
                second=convert_type(match.group(3)),
            )
        elif operator in [">>", "<<"]:
            cause = _(
                "        You tried to perform the bit shifting operation {operator}\n"
                "        on two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                operator=operator,
                first=convert_type(match.group(2)),
                second=convert_type(match.group(3)),
            )
        elif operator == "** or pow()":
            cause = _(
                "        You tried to exponentiate (raise to a power)\n"
                "        using two incompatible types of objects:\n"
                "        {first} and {second}\n"
            ).format(
                first=convert_type(match.group(2)), second=convert_type(match.group(3))
            )
    return cause


# example: '<' not supported between instances of 'int' and 'str'
order_comparison_pattern = re.compile(
    r"[\'\"](.+)[\'\"] not supported between instances of [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"  # noqa
)


@add_cause
def parse_order_comparison(text):
    _ = current_lang.lang
    match = re.search(order_comparison_pattern, text)
    if match is not None:
        cause = _(
            "        You tried to do an order comparison ({operator})\n"
            "        between two incompatible types of objects:\n"
            "        {first} and {second}\n"
        ).format(
            operator=match.group(1),
            first=convert_type(match.group(2)),
            second=convert_type(match.group(3)),
        )
        return cause
    else:
        return None
