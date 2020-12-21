"""type_error.py

Collection of functions useful in parsing TypeError messages and
providing a more detailed explanation.
"""

import re

from ..my_gettext import current_lang
from .. import utils
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


@add_message_parser
def parse_can_only_concatenate(message, *args):
    _ = current_lang.translate
    cause = hint = None
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(
        r"can only concatenate (\w+) \(not [\'\"](\w+)[\'\"]\) to (\w+)"
    )
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}\n"
        ).format(
            first=convert_type(match.group(1)), second=convert_type(match.group(2))
        )
    return cause, hint


@add_message_parser
def parse_must_be_str(message, *args):
    _ = current_lang.translate
    cause = hint = None
    # python 3.6 version: must be str, not int
    # example: can only concatenate str (not "int") to str
    pattern = re.compile(r"must be str, not (\w+)")
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}\n"
        ).format(first=convert_type("str"), second=convert_type(match.group(1)))
    return cause, hint


@add_message_parser
def parse_unsupported_operand_type(message, *args):
    _ = current_lang.translate
    cause = hint = None
    # example: unsupported operand type(s) for +: 'int' and 'str'
    pattern = re.compile(
        r"unsupported operand type\(s\) for (.+): [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"
    )
    match = re.search(pattern, message)
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
    return cause, hint


@add_message_parser
def parse_order_comparison(message, *args):
    _ = current_lang.translate
    cause = hint = None
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
    return cause, hint


@add_message_parser
def bad_operand_type_for_unary(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    # example: bad operand type for unary +: 'str'
    pattern = re.compile(r"bad operand type for unary (.+): [\'\"](\w+)[\'\"]")
    match = re.search(pattern, message)
    if match is not None:
        # The user might have written something like "=+" instead of
        # "+="
        operator = match.group(1)
        index = utils.find_substring_index(tb_data.original_bad_line, tb_data.bad_line)
        if index > 0:
            tokens = utils.tokenize_source(tb_data.original_bad_line)
            if (
                tokens[index - 1].string == "="
                and tokens[index - 1].end_col == tokens[index].start_col
            ):
                hint = _(
                    "Perhaps you meant to write `{operator}=` instead of `={operator}`"
                ).format(operator=operator)

        cause = _(
            "You tried to use the unary operator '{operator}'\n"
            "with the following type of object: {obj}.\n"
            "This operation is not defined for this type of object.\n"
        ).format(operator=operator, obj=convert_type(match.group(2)))
        if hint is not None:
            cause += "\n" + hint + "\n"
    return cause, hint


@add_message_parser
def does_not_support_item_asssignment(message, *args):
    _ = current_lang.translate
    cause = hint = None
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
    return cause, hint


@add_message_parser
def exception_derived_from_BaseException(message, *args):
    _ = current_lang.translate
    cause = hint = None

    if "exceptions must derive from BaseException" in message:
        cause = _("In Python 3, exceptions must be derived from BaseException.\n")
    return cause, hint


@add_message_parser
def incorrect_nb_positional_arguments(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    # example: my_function() takes 0 positional arguments but x was/were given
    pattern = re.compile(r"(.*) takes (\d+) positional argument[s]* but (\d+) ")
    match = re.search(pattern, message)

    if match is not None:
        fn_name = match.group(1)[:-2]
        nb_required = match.group(2)
        nb_given = match.group(3)
        if int(nb_given) - int(nb_required) == 1:
            # Python 3.10
            if "." in fn_name:
                missing_self = True
            else:
                tokens = utils.tokenize_source(tb_data.bad_line)
                prev_token = tokens[0]
                missing_self = False
                for token in tokens:
                    if token == fn_name and prev_token == ".":
                        missing_self = True
                        break
                    prev_token = token

        if ".<locals>." in fn_name:
            fn_name = fn_name.split(".<locals>.")[1]
        cause = _(
            "You apparently have called the function `{fn_name}` with\n"
            "{nb_given} positional argument(s) while it requires {nb_required}\n"
            "such positional argument(s).\n"
        ).format(fn_name=fn_name, nb_given=nb_given, nb_required=nb_required)
        if missing_self:
            hint = _("Perhaps you forgot `self` when defining `{fn_name}`.\n").format(
                fn_name=fn_name
            )
            cause += hint
    return cause, hint


@add_message_parser
def missing_positional_arguments(message, *args):
    _ = current_lang.translate
    cause = hint = None
    # example: my_function() missing 1 required positional argument
    pattern = re.compile(r"(.*) missing (\d+) required positional argument")
    match = re.search(pattern, message)

    if match is not None:
        cause = _(
            "You apparently have called the function '{fn_name}' with\n"
            "fewer positional arguments than it requires ({nb_required} missing).\n"
        ).format(fn_name=match.group(1), nb_required=match.group(2))
    return cause, hint


@add_message_parser
def x_is_not_callable(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"'(.*)' object is not callable")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    obj_type = match.group(1)

    # Start with default cause, in case we cannot do better
    cause = _(
        "Python indicates that you have an object of type `{obj_type}`,\n"
        "followed by something surrounded by parentheses, `(...)`,\n"
        "which Python took as an indication of a function call.\n"
        "Either the object of type {obj_type} was meant to be a function,\n"
        "or you forgot a comma before `(...)`.\n"
    ).format(obj_type=obj_type)

    obj = info_variables.get_object_from_name(obj_type, frame)
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for obj_name, instance in all_objects:
        if isinstance(instance, obj) or instance == obj:
            fn_call = tb_data.bad_line.replace(obj_name, "", 1).strip()
            if fn_call.startswith("(") and fn_call.endswith(")"):
                break
    else:
        return cause, hint

    cause = _(
        "Because of the surrounding parenthesis, `{fn_call}` \n"
        "is interpreted by Python as indicating a function call for \n"
        "`{obj_name}`, which is an object of type `{obj_type}`\n"
        "which cannot be called.\n\n"
    ).format(fn_call=fn_call, obj_name=obj_name, obj_type=obj_type)

    try:
        can_eval = eval(fn_call, frame.f_globals, frame.f_locals)
    except Exception:
        return cause, hint

    if isinstance(can_eval, tuple):
        cause = cause + _(
            "However, `{fn_call}` is a `tuple`.\n"
            "Either the object `{obj_name}` was meant to be a function\n"
            "or you have a missing comma between the object `{obj_name}`\n"
            "and the tuple `{fn_call}` and meant to write\n"
            "`{obj_name}, {fn_call}`.\n"
        ).format(fn_call=fn_call, obj_name=obj_name)
        hint = _(
            "Did you forget a comma between `{obj_name}` and `{fn_call}`?\n"
        ).format(fn_call=fn_call, obj_name=obj_name)
        return cause, hint

    elif hasattr(obj, "__getitem__") and isinstance(can_eval, int):
        cause = cause + _(
            "However, `{obj_name}` is a sequence.\n"
            "Perhaps you meant to use `[]` instead of `()` and write\n"
            "`{obj_name}[{slice}]`\n"
        ).format(obj_name=obj_name, slice=fn_call[1:-1])
        hint = _("Did you mean `{obj_name}[{slice}]`?\n").format(
            obj_name=obj_name, slice=fn_call[1:-1]
        )
        return cause, hint

    elif (  # Many objects can be multipled, but only numbers should have __abs__
        hasattr(obj, "__abs__")  # Should identify numbers: int, float, ...
        and hasattr(can_eval, "__abs__")  # complex, Fractions, Decimals, ...
        and hasattr(obj, "__mul__")  # Confirming that they can be multiplied
        and hasattr(can_eval, "__mul__")
    ):
        cause = cause + _(
            "However, both `{obj_name}` and `{fn_call}` are numbers.\n"
            "Perhaps you forgot a multiplication operator, `*`,\n"
            "and meant to write `{obj_name} * {fn_call}`\n."
        ).format(fn_call=fn_call, obj_name=obj_name)
        hint = _("Did you mean `{obj_name} * {fn_call}`?\n").format(
            fn_call=fn_call, obj_name=obj_name
        )
        return cause, hint

    return cause, hint


@add_message_parser
def cannot_multiply_by_str(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    if "can't multiply sequence by non-int of type 'str'" in message:
        cause = _(
            "You can only multiply sequences, such as list, tuples,\n "
            "strings, etc., by integers.\n"
        )
        names = find_possible_integers(str, frame, tb_data.bad_line)
        if names:
            tokens = utils.tokenize_source(tb_data.bad_line)
            int_vars = []
            for prev_token, token in zip(tokens, tokens[1:]):
                if prev_token.string in ["*", "*="] and token.string in names:
                    int_vars.append(token.string)
                elif prev_token.string in names and token == "*":
                    int_vars.append(prev_token.string)
                else:
                    continue
            if not int_vars:  # should not happen, but better be safe
                return cause, hint
            elif len(int_vars) == 1:
                name = int_vars[0]
                hint = _(
                    "Did you forget to convert `{name}` into an integer?\n"
                ).format(name=name)
                cause += _(
                    "Perhaps you forgot to convert `{name}` into an integer.\n"
                ).format(name=name)
            else:
                hint = _(
                    "Did you forget to convert `{name1}` and `{name2}` into integers?\n"
                ).format(name1=int_vars[0], name2=int_vars[1])
                cause += _(
                    "Perhaps you forgot to convert `{name1}` and `{name2}` into integers.\n"
                ).format(name1=int_vars[0], name2=int_vars[1])
            return cause, hint

    return cause, hint


def find_possible_integers(object_of_type, frame, line):
    all_objects = info_variables.get_all_objects(line, frame)
    names = []
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, object_of_type):
            try:
                int(obj)
                names.append(name)
            except Exception:
                pass

    return names


@add_message_parser
def object_cannot_be_interpreted_as_an_integer(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"'(.*)' object cannot be interpreted as an integer")
    match = re.search(pattern, message)
    if match is not None:
        obj_name = match.group(1)
        object_of_type = info_variables.get_object_from_name(obj_name, frame)
        if object_of_type is None:
            return cause, hint

        names = find_possible_integers(object_of_type, frame, tb_data.bad_line)

        cause = _(
            "You wrote an object of type `{obj}` where an integer was expected.\n"
        ).format(obj=obj_name)

        if names:
            if len(names) == 1:
                name = names[0]
                hint = _(
                    "Did you forget to convert `{name}` into an integer?\n"
                ).format(name=name)
                cause += _(
                    "Perhaps you forgot to convert `{name}` into an integer."
                ).format(name=name)
            else:
                names = [name for name in names]
                names = ", ".join(names)
                hint = _("Did you forget to convert `{names}` into integers?\n").format(
                    names=names
                )
                cause += _(
                    "Perhaps you forgot to convert `{names}` into integers."
                ).format(names=names)

    return cause, hint
