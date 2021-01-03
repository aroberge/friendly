"""type_error.py

Collection of functions useful in parsing TypeError messages and
providing a more detailed explanation.
"""

import re

from ..my_gettext import current_lang
from .. import info_variables
from .. import debug_helper
from .. import token_utils

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
        return None, None


def _get_cause(value, frame, tb_data):
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
    # TODO: add hint if one of them could be converted to make this possible
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}.\n"
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

    # TODO: add hint if one of them could be converted to make this possible
    # also see if can be generalized

    pattern = re.compile(r"must be str, not (\w+)")
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to concatenate (add) two different types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type("str"), second=convert_type(match.group(1)))
    return cause, hint


def _convert_str_to_number(obj_type1, obj_type2, operator, frame, tb_data):
    """Determines if a suggestion should be made to convert a string to a
    number type; potentially useful for beginners that write programs
    that use input() and ask for numbers.

    So, we want to give hints in cases like 'number + string',
    'string + number', 'number += string', but not 'string += number'
    """
    _ = current_lang.translate
    cause = hint = None
    types = obj_type1, obj_type2
    if "str" not in types or obj_type1 == "str" and "=" in operator:
        return cause, hint

    if not ("int" in types or "float" in types or "complex" in types):
        return cause, hint

    types_str = ["int", "float", "complex"]
    types_fn = [int, float, complex]

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for name, obj in all_objects:
        if isinstance(obj, str):
            for number_type, fn in zip(types_str, types_fn):
                try:
                    fn(obj)
                    break
                except Exception:
                    pass
            else:
                return cause, hint

    hint = _(
        "Did you forget to convert the string `{name}` into {number_type}?\n"
    ).format(name=name, number_type=convert_type(number_type))
    cause = _(
        "Perhaps you forgot to convert the string `{name}` into {number_type}.\n"
    ).format(name=name, number_type=convert_type(number_type))
    return cause, hint


@add_message_parser
def parse_unsupported_operand_type(message, frame, tb_data):
    _ = current_lang.translate
    more_cause = cause = hint = None
    # example: unsupported operand type(s) for +: 'int' and 'str'
    pattern = re.compile(
        r"unsupported operand type\(s\) for (.+): [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"
    )
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    # TODO: look if can be done by converting from str to other type.
    # think of adding hint if that is the case.

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    operator = match.group(1)
    obj_type1 = match.group(2)
    obj_type2 = match.group(3)
    if operator in ["+", "+="]:
        cause = _(
            "You tried to add two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, operator, frame, tb_data
        )
    elif operator in ["-", "-="]:
        cause = _(
            "You tried to subtract two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, operator, frame, tb_data
        )
    elif operator in ["*", "*="]:
        cause = _(
            "You tried to multiply two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, operator, frame, tb_data
        )
    elif operator in ["/", "//", "/=", "//="]:
        cause = _(
            "You tried to divide two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, operator, frame, tb_data
        )
    elif operator in ["&", "|", "^", "&=", "|=", "^="]:
        cause = _(
            "You tried to perform the bitwise operation {operator}\n"
            "on two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(
            operator=operator,
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )
        if "^" in operator:
            can_exponentiate = True
            for name, obj in all_objects:
                if not hasattr(obj, "__pow__"):
                    can_exponentiate = False
                    break
            if can_exponentiate:
                line = tb_data.bad_line.replace("^", "**").strip()
                hint = _("Did you mean `{line}`?\n").format(line=line)
                cause += _(
                    "Outside of Python, `^` is often used to indicate exponentiation.\n"
                )
                cause += _("Perhaps you meant `{line}`.\n").format(line=line)

    elif operator in [">>", "<<", ">>=", "<<="]:
        cause = _(
            "You tried to perform the bit shifting operation {operator}\n"
            "on two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(
            operator=operator,
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )
    elif operator == "** or pow()":
        cause = _(
            "You tried to exponentiate (raise to a power)\n"
            "using two incompatible types of objects:\n"
            "{first} and {second}.\n"
        ).format(first=convert_type(obj_type1), second=convert_type(obj_type2))
        more_cause, possible_hint = _convert_str_to_number(
            obj_type1, obj_type2, operator, frame, tb_data
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
            first=convert_type(obj_type1),
            second=convert_type(obj_type2),
        )

    if more_cause is not None:
        cause += more_cause
        hint = possible_hint
    return cause, hint


@add_message_parser
def parse_order_comparison(message, *args):
    _ = current_lang.translate
    cause = hint = None
    # example: '<' not supported between instances of 'int' and 'str'
    pattern = re.compile(
        r"[\'\"](.+)[\'\"] not supported between instances of [\'\"](\w+)[\'\"] and [\'\"](\w+)[\'\"]"  # noqa
    )
    # TODO: check if one is string that could be converted to number
    match = re.search(pattern, message)
    if match is not None:
        cause = _(
            "You tried to do an order comparison ({operator})\n"
            "between two incompatible types of objects:\n"
            "{first} and {second}.\n"
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
        index = token_utils.find_substring_index(
            tb_data.original_bad_line, tb_data.bad_line
        )
        if index > 0:
            tokens = token_utils.get_significant_tokens(tb_data.original_bad_line)
            if (
                tokens[index - 1] == "="
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
        name = match.group(1)
        cause = _(
            "In Python, some objects are known as immutable:\n"
            "once defined, their value cannot be changed.\n"
            "You tried change part of such an immutable object: {obj},\n"
            "most likely by using an indexing operation.\n"
        ).format(obj=convert_type(name))
        if name == "tuple" or name == "set":
            hint = _("Did you mean to use a list?\n")
            cause += _("Perhaps you meant to use a list instead.\n")
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
        if ".<locals>." in fn_name:
            fn_name = fn_name.split(".<locals>.")[1]
        if int(nb_given) - int(nb_required) == 1:
            # Python 3.10
            if "." in fn_name:
                missing_self = True
            else:
                tokens = token_utils.get_significant_tokens(tb_data.bad_line)
                prev_token = tokens[0]
                missing_self = False
                for token in tokens:
                    if token == fn_name and prev_token == ".":
                        missing_self = True
                        break
                    prev_token = token
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


def forgot_to_convert_name_to_int(name):
    """Explanations common to many cases about converting a single
    name to an integer.
    """
    _ = current_lang.translate
    hint = _("Did you forget to convert `{name}` into an integer?\n").format(name=name)
    additional_cause = _(
        "Perhaps you forgot to convert `{name}` into an integer.\n"
    ).format(name=name)
    return additional_cause, hint


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
            tokens = token_utils.get_significant_tokens(tb_data.bad_line)
            int_vars = []
            for prev_token, token in zip(tokens, tokens[1:]):
                if prev_token.is_in(["*", "*="]) and token.is_in(names):
                    int_vars.append(token.string)
                elif prev_token.is_in(names) and token == "*":
                    int_vars.append(prev_token.string)
                else:
                    continue
            if not int_vars:  # should not happen, but better be safe
                return cause, hint
            elif len(int_vars) == 1:
                more_cause, hint = forgot_to_convert_name_to_int(int_vars[0])
                cause += more_cause
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
                more_cause, hint = forgot_to_convert_name_to_int(names[0])
                cause += more_cause
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


@add_message_parser
def indices_must_be_integers_or_slices(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"(.*) indices must be integers or slices, not (.*)")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    container_type = match.group(1)
    index_type = match.group(2)
    cause = _(
        "In the expression `{line}`\n"
        "what is included between the square brackets, `[...]`,\n"
        "must be either an integer or a slice\n"
        "(`start:stop` or `start:stop:step`) \n"
        "and you have used {obj_type} instead.\n"
    ).format(line=tb_data.bad_line, obj_type=convert_type(index_type))

    # To see if we can get more specific info,
    # we assume we have container[...]
    # and we look for two cases:
    # 1. if ... is a tuple, if we replace commas by colons (, --> :)
    #    do we get a valid expression.
    # 2. if ... is something of another type that can be converted into an integer
    try:
        container_type = eval(container_type, frame.f_globals, frame.f_locals)
    except Exception:
        return cause, hint

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, container_type) and tb_data.bad_line.startswith(name):
            container = name
            break
    else:
        return cause, hint

    index = tb_data.bad_line.replace(container, "", 1)
    if not (index.startswith("[") and index.endswith("]")):
        return cause, hint

    index = index[1:-1]
    try:
        index = eval(index, frame.f_globals, frame.f_locals)
        index_type = eval(index_type)
    except Exception:
        return cause, hint

    if not isinstance(index, index_type):
        return cause, hint

    if isinstance(index, tuple):
        # container[a, b] --> [][a: b]
        newline = tb_data.bad_line.replace(container, "[]", 1).replace(",", ":")
        try:
            result = [] == eval(newline, frame.f_globals, frame.f_locals)
        except Exception:
            result = False

        if not result:
            return cause, hint

        hint = _("Did you mean `{line}`?\n").format(
            line=container + newline.replace("[]", "", 1)
        )
        cause += "\n" + _("Perhaps you meant `{line}`.\n").format(
            line=container + newline.replace("[]", "", 1)
        )
    elif isinstance(index, index_type):
        names = find_possible_integers(index_type, frame, tb_data.bad_line)
        if len(names) == 1:  # This should usually be the case
            more_cause, hint = forgot_to_convert_name_to_int(names[0])
            cause += "\n" + more_cause
            return cause, hint

    return cause, hint


@add_message_parser
def slice_indices_must_be_integers_or_None(message, *args):
    _ = current_lang.translate
    cause = hint = None
    if message != (
        "slice indices must be integers or None or have an __index__ method"
    ):
        return cause, hint

    cause = _(
        "When using a slice to extract a range of elements\n"
        "from a sequence, that is something like\n"
        "`[start:stop]` or `[start:stop:step]`\n"
        "each of `start`, `stop`, `step` must be either an integer, `None`,\n"
        "or possibly some other object having an `__index__` method.\n"
    )
    return cause, hint


@add_message_parser
def unhashable_type(message, *args):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"unhashable type: '(.*)'")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    cause = _(
        "Unhashable objects are objects that do not change value\n"
        "once they are created. Only unhashable objects can be used\n"
        "as elements of `set` or keys of `dict`.\n"
    )

    original = match.group(1)
    replacements = {"list": "tuple", "set": "frozenset"}
    if original in replacements:
        cause += _(
            "Instead of using {original}, consider using {replacement}.\n"
        ).format(
            original=convert_type(original),
            replacement=convert_type(replacements[original]),
        )

    return cause, hint


@add_message_parser
def object_is_not_subscriptable(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"'(.*)' object is not subscriptable")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    obj_type = match.group(1)

    cause = _(
        "Subscriptable objects are typically containers from which\n"
        "you can retrieve item using the notation `[...]`.\n"
    )

    # first, try to identify object
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        truncated = tb_data.bad_line.replace(name, "", 1)
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:
        cause += _(
            "Using this notation, you attempted to retrieve an item\n"
            "from an object of type `{obj_type}` which is not allowed.\n"
        ).format(obj_type=obj_type)
        return cause, hint

    if callable(obj):
        line = name + "(" + truncated[1:-1] + ")"
        hint = _("Did you mean `{line}`?\n").format(line=line)
        cause += "\n" + _("Perhaps you meant to write `{line}`.\n").format(line=line)
        return cause, hint

    cause += _(
        "Using this notation, you attempted to retrieve an item\n"
        "from `{name}`, an object of type `{obj_type}`. This is not allowed.\n"
    ).format(obj_type=obj_type, name=name)

    return cause, hint


@add_message_parser
def object_is_not_iterable(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"'(.*)' object is not iterable")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    cause = _(
        "An iterable is an object capable of returning its members one at a time.\n"
        "Python containers (`list, tuple, dict`, etc.) are iterables.\n"
        "An iterable is required here.\n"
    )
    return cause, hint


@add_message_parser
def cannot_unpack_non_iterable(message, *args):
    _ = current_lang.translate
    cause = hint = None
    pattern = re.compile(r"cannot unpack non-iterable (.*) object")
    match = re.search(pattern, message)
    if match is None:
        return cause, hint

    cause = _(  # reusing definition from elsewhere
        "Unpacking is a convenient way to assign a name,\n"
        "to each item of an iterable.\n"
    )
    cause += _(
        "An iterable is an object capable of returning its members one at a time.\n"
        "Python containers (`list, tuple, dict`, etc.) are iterables,\n"
        "but not objects of type `{obj_type}`.\n"
    ).format(obj_type=match.group(1))
    return cause, hint


@add_message_parser
def cannot_convert_dictionary_update_sequence(message, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None
    if "cannot convert dictionary update sequence element" not in message:
        return cause, hint

    possible_cause = _(
        "{function} does not accept a sequence as an argument.\n"
        "Instead of writing `{line}`\n"
        "perhaps you should use the `dict.fromkeys()` method: `{new_line}`.\n"
    )
    possible_hint = _("Perhaps you need to use the `dict.fromkeys()` method.\n")

    bad_line = tb_data.bad_line
    if bad_line.startswith("dict("):
        cause = possible_cause.format(
            function="`dict()`",
            line=bad_line,
            new_line=bad_line.replace("dict(", "dict.fromkeys(", 1),
        )
        hint = possible_hint
    elif ".update(" in bad_line:
        cause = possible_cause.format(
            function="`dict.update()`",
            line=bad_line,
            new_line=bad_line.replace(".update(", ".update( dict.fromkeys(", 1) + " )",
        )
        hint = possible_hint

    return cause, hint
