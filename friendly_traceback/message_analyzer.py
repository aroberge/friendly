"""message_analyser.py

Collection of functions that examine SyntaxError messages and
return relevant information to users.
"""
from keyword import kwlist
import re
import sys
import tokenize

from .my_gettext import current_lang
from . import utils
from . import source_analyzer
from .friendly_exception import FriendlyException


MESSAGE_ANALYZERS = []

# The following has been taken from https://unicode-table.com/en/sets/quotation-marks/
bad_quotation_marks = [
    "«",
    "»",
    "‹",
    "›",
    "„",
    "“",
    "‟",
    "”",
    "’",
    "❝",
    "❞",
    "❮",
    "❯",
    "⹂",
    "〝",
    "〞",
    "＂",
    "‚",
    "‘",
    "‛",
    "❛",
    "❜",
    "❟",
]


def analyze_message(message="", line="", linenumber=0, source_lines=None, offset=0):
    for case in MESSAGE_ANALYZERS:
        cause = case(
            message=message,
            line=line,
            linenumber=linenumber,
            source_lines=source_lines,
            offset=offset,
        )
        if cause:
            return cause


def add_python_message(func):
    """A simple decorator that adds a function the the list of functions
       that process a message given by Python.
    """
    MESSAGE_ANALYZERS.append(func)

    def wrapper(**kwargs):
        return func(**kwargs)

    return wrapper


@add_python_message
def assign_to_keyword(message="", line="", **kwargs):
    _ = current_lang.translate
    if not (
        message == "can't assign to keyword"  # Python 3.6, 3.7
        or message == "assignment to keyword"  # Python 3.6, 3.7
        or message == "cannot assign to keyword"  # Python 3.8
        or message == "cannot assign to None"  # Python 3.8
        or message == "cannot assign to True"  # Python 3.8
        or message == "cannot assign to False"  # Python 3.8
        or message == "cannot assign to __debug__"  # Python 3.8
        or message == "can't assign to Ellipsis"  # Python 3.6, 3.7
        or message == "cannot assign to Ellipsis"  # Python 3.8
        or message == "cannot use named assignment with True"  # Python 3.8
        or message == "cannot use named assignment with False"  # Python 3.8
        or message == "cannot use named assignment with None"  # Python 3.8
        or message == "cannot use named assignment with Ellipsis"  # Python 3.8
        or message == "cannot use assignment expressions with True"  # Python 3.8
        or message == "cannot use assignment expressions with False"  # Python 3.8
        or message == "cannot use assignment expressions with None"  # Python 3.8
        or message == "cannot use assignment expressions with Ellipsis"  # Python 3.8
    ):
        return

    if "Ellipsis" in message:
        word = "Ellipsis (...)"
    else:
        tokens = utils.tokenize_source(line)
        while True:
            for token in tokens:
                word = token.string
                if word in kwlist or word == "__debug__":
                    break
            else:
                raise FriendlyException("analyze_syntax.assign_to_keyword")
            break

    if word in ["None", "True", "False", "__debug__", "Ellipsis (...)"]:
        return _(
            "`{keyword}` is a constant in Python; you cannot assign it a value.\n" "\n"
        ).format(keyword=word)
    else:
        return _(
            "You were trying to assign a value to the Python keyword `{keyword}`.\n"
            "This is not allowed.\n"
            "\n"
        ).format(keyword=word)


@add_python_message
def assign_to_conditional_expression(message="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to conditional expression"  # Python 3.6, 3.7
        or message == "cannot assign to conditional expression"  # Python 3.8
    ):
        return _(
            "On the left-hand side of an equal sign, you have a\n"
            "conditional expression instead of the name of a variable.\n"
            "A conditional expression has the following form:\n\n"
            "    variable = object if condition else other_object"
        )


@add_python_message
def assign_to_function_call(message="", line="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to function call"  # Python 3.6, 3.7
        or message == "cannot assign to function call"  # Python 3.8
    ):
        if line.count("=") > 1:
            # we have something like  fn(a=1) = 2
            # or fn(a) = 1 = 2, etc.  Since there could be too many
            # combinations, we use some generic names
            fn_call = _("my_function(...)")
            value = _("some value")
            return _(
                "You wrote an expression like\n\n"
                "    {fn_call} = {value}\n\n"
                "where `{fn_call}`, on the left-hand side of the equal sign, is\n"
                "a function call and not the name of a variable.\n"
            ).format(fn_call=fn_call, value=value)

        info = line.split("=")
        fn_call = info[0].strip()
        value = info[1].strip()
        return _(
            "You wrote the expression\n\n"
            "    {fn_call} = {value}\n\n"
            "where `{fn_call}`, on the left-hand side of the equal sign, either is\n"
            "or includes a function call and is not simply the name of a variable.\n"
        ).format(fn_call=fn_call, value=value)


@add_python_message
def assign_to_generator_expression(message="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to generator expression"  # Python 3.6, 3.7
        or message == "cannot assign to generator expression"  # Python 3.8
    ):
        return _(
            "On the left-hand side of an equal sign, you have a\n"
            "generator expression instead of the name of a variable.\n"
        )


def what_kind_of_literal(literal):
    _ = current_lang.translate

    try:
        a = eval(literal)
    except Exception:
        return None

    if isinstance(a, int):
        return _("of type `int`")
    elif isinstance(a, str):
        return _("of type `str`")
    elif isinstance(a, float):
        return _("of type `float`")
    elif isinstance(a, complex):
        return _("of type `complex`")
    elif isinstance(a, dict):
        return _("of type `dict`")
    elif isinstance(a, tuple):
        return _("of type `tuple`")
    elif isinstance(a, list):
        return _("of type `list`")
    elif isinstance(a, set):
        return _("of type `set`")
    else:
        return None


@add_python_message
def assign_to_f_expression(message="", line="", **kwargs):
    _ = current_lang.translate
    if message == "cannot assign to f-string expression":
        return _(
            "You wrote an expression that has an f-string\n"
            "on the left-hand side of the equal sign.\n"
            "An f-string should only appear on the right-hand"
            "side of the equal sign.\n"
        )


@add_python_message
def assign_to_literal(message="", line="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to literal"  # Python 3.6, 3.7
        or message == "cannot assign to literal"  # Python 3.8
        or message == "cannot assign to set display"  # Python 3.8
        or message == "cannot assign to dict display"  # Python 3.8
    ):
        info = line.split("=")
        if len(info) == 2:
            literal = info[0].strip()
            name = info[1].strip()
            if sys.version_info < (3, 8) and (
                literal.startswith("f'{") or literal.startswith('f"{')
            ):
                return _(
                    "You wrote an expression that has an f-string\n"
                    "on the left-hand side of the equal sign.\n"
                    "An f-string should only appear on the right-hand"
                    "side of the equal sign\n."
                )
        else:
            literal = None
            name = _("variable_name")

        if len(info) == 2 and name.isidentifier():
            # fmt: off
            suggest = _(
                " Perhaps you meant to write:\n\n"
                "    {name} = {literal}\n"
                "\n"
            ).format(literal=literal, name=name)
            # fmt: on
        else:
            suggest = "\n"

        # Impose the right type when we know it.
        if message == "cannot assign to set display":
            of_type = what_kind_of_literal("{1}")
        elif message == "cannot assign to dict display":
            of_type = what_kind_of_literal("{1:2}")
        else:
            of_type = what_kind_of_literal(literal)
        if of_type is None:
            of_type = ""

        if literal is None:
            literal = "..."

        return (
            _(
                "You wrote an expression like\n\n"
                "    {literal} = {name}\n"
                "where `{literal}`, on the left-hand side of the equal sign,\n"
                "is or includes an actual object {of_type}\n"
                "and is not simply the name of a variable."
            ).format(literal=literal, name=name, of_type=of_type)
            + suggest
        )


@add_python_message
def assign_to_operator(message="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to operator"  # Python 3.6, 3.7
        or message == "cannot assign to operator"  # Python 3.8
    ):
        return _(
            "You wrote an expression that includes some mathematical operations\n"
            "on the left-hand side of the equal sign which should be\n"
            "only used to assign a value to a variable."
        )


@add_python_message
def both_nonlocal_and_global(message="", line=None, **kwargs):
    _ = current_lang.translate
    if "is nonlocal and global" in message:
        name = message.split("'")[1]
        return _(
            "You declared `{name}` as being both a global and nonlocal variable.\n"
            "A variable can be global, or nonlocal, but not both at the same time.\n"
        ).format(name=name)


@add_python_message
def break_outside_loop(message="", **kwargs):
    _ = current_lang.translate
    if "'break' outside loop" in message:
        return _(
            "The Python keyword `break` can only be used "
            "inside a for loop or inside a while loop.\n"
        )


@add_python_message
def continue_outside_loop(message="", **kwargs):
    _ = current_lang.translate
    if "'continue' not properly in loop" in message:
        return _(
            "The Python keyword `continue` can only be used "
            "inside a for loop or inside a while loop.\n"
        )


@add_python_message
def delete_function_call(message="", line=None, **kwargs):
    _ = current_lang.translate
    if (
        message == "can't delete function call"  # Python 3.6, 3.7
        or message == "cannot delete function call"  # Python 3.8
    ):
        tokens = utils.tokenize_source(line)
        if (
            tokens[0].string == "del"
            and tokens[1].type == tokenize.NAME
            and tokens[2].string == "("
            and tokens[-1].string == ")"
        ):
            correct = "del {name}".format(name=tokens[1].string)
        else:
            line = "del function()"
            correct = "del function"
        return _(
            "You attempted to delete a function call\n\n"
            "    {line}\n"
            "instead of deleting the function's name\n\n"
            "    {correct}\n"
        ).format(line=line, correct=correct)


@add_python_message
def duplicate_argument_in_function_definition(message="", line=None, **kwargs):
    _ = current_lang.translate
    if "duplicate argument" in message and "function definition" in message:
        name = message.split("'")[1]
        return _(
            "You have defined a function repeating the keyword argument\n\n"
            "    {name}\n"
            "twice; each keyword argument should appear only once"
            " in a function definition.\n"
        ).format(name=name)


@add_python_message
def eol_while_scanning_string_literal(message="", **kwargs):
    _ = current_lang.translate
    if "EOL while scanning string literal" in message:
        return _(
            "You starting writing a string with a single or double quote\n"
            "but never ended the string with another quote on that line.\n"
        )


@add_python_message
def expression_cannot_contain_assignment(message="", **kwargs):
    _ = current_lang.translate
    if "expression cannot contain assignment, perhaps you meant" in message:
        return _(
            "One of the following two possibilities could be the cause:\n"
            "1. You meant to do a comparison with == and wrote = instead.\n"
            "2. You called a function with a named argument:\n\n"
            "       a_function(invalid=something)\n\n"
            "where `invalid` is not a valid variable name in Python\n"
            "either because it starts with a number, or is a string,\n"
            "or contains a period, etc.\n"
            "\n"
        )


@add_python_message
def generator_expression_must_be_parenthesized(message="", **kwargs):
    _ = current_lang.translate
    if "Generator expression must be parenthesized" in message:
        return _(
            "You are using a generator expression, something of the form\n"
            "    `x for x in thing`\n"
            "You must add parentheses enclosing that expression.\n"
        )


@add_python_message
def keyword_argument_repeated(message="", **kwargs):
    _ = current_lang.translate
    if "keyword argument repeated" in message:
        return _(
            "You have called a function repeating the same keyword argument.\n"
            "Each keyword argument should appear only once in a function call.\n"
        )


@add_python_message
def keyword_cannot_be_expression(message="", **kwargs):
    _ = current_lang.translate
    if "keyword can't be an expression" in message:
        return _(
            "You likely called a function with a named argument:\n\n"
            "   `a_function(invalid=something)`\n\n"
            "where `invalid` is not a valid variable name in Python\n"
            "either because it starts with a number, or is a string,\n"
            "or contains a period, etc.\n"
            "\n"
        )


@add_python_message
def invalid_character_in_identifier(message="", line="", **kwargs):
    _ = current_lang.translate
    copy_paste = _("Did you use copy-paste?\n")
    if "invalid character" in message:
        if sys.version_info >= (3, 9):
            if "'" in message:
                parts = message.split("'")
                bad_character = parts[1]
                result = _(
                    "Python indicates that you used the unicode character"
                    " `{bad_character}`\n"
                    "which is not allowed.\n"
                ).format(bad_character=bad_character)
                if bad_character in bad_quotation_marks:
                    return (
                        copy_paste
                        + result
                        + _(
                            "I suspect that you used a fancy unicode quotation mark\n"
                            "instead of a normal single or double quote for a string."
                            "\n"
                        )
                    )
                else:
                    return result

        for quote in bad_quotation_marks:
            if quote in line:
                return _(
                    "Python indicates that you used some unicode characters not allowed\n"
                    "as part of a variable name; this includes many emojis.\n"
                    "However, I suspect that you used a fancy unicode quotation mark\n"
                    "instead of a normal single or double quote for a string.\n"
                    "This can happen if you copy-pasted code.\n"
                    "\n"
                )
        return _(
            "You likely used some unicode character that is not allowed\n"
            "as part of a variable name in Python.\n"
            "This includes many emojis.\n"
            "\n"
        )


@add_python_message
def mismatched_parenthesis(
    message="", source_lines=None, linenumber=None, offset=None, **kwargs
):
    # Python 3.8; something like:
    # closing parenthesis ']' does not match opening parenthesis '(' on line
    _ = current_lang.translate
    pattern1 = re.compile(
        r"closing parenthesis '(.)' does not match opening parenthesis '(.)' on line (\d+)"
    )
    match = re.search(pattern1, message)
    if match is None:
        lineno = None
        pattern2 = re.compile(
            r"closing parenthesis '(.)' does not match opening parenthesis '(.)'"
        )
        match = re.search(pattern2, message)
        if match is None:
            return
    else:
        lineno = match.group(3)

    opening = match.group(2)
    closing = match.group(1)

    if lineno is not None:
        response = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}` on line {lineno}.\n\n"
        ).format(closing=closing, opening=opening, lineno=lineno)
    else:
        response = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}`.\n\n"
        ).format(closing=closing, opening=opening)

    additional_response = source_analyzer.look_for_mismatched_brackets(
        source_lines=source_lines, max_linenumber=linenumber, offset=offset
    )

    if additional_response:
        response += (
            _("I will attempt to be give a bit more information.\n\n")
            + additional_response
        )

    return response


@add_python_message
def unterminated_f_string(message="", **kwargs):
    _ = current_lang.translate
    if "f-string: unterminated string" in message:
        return _(
            "Inside an f-string, which is a string prefixed by the letter f, \n"
            "you have another string, which starts with either a\n"
            "single quote (') or double quote (\"), without a matching closing one.\n"
        )


@add_python_message
def name_is_parameter_and_global(message="", line="", **kwargs):
    # something like: name 'x' is parameter and global
    _ = current_lang.translate
    if "is parameter and global" in message:
        name = message.split("'")[1]
        if name in line and "global" in line:
            newline = line
        else:
            newline = f"global {name}"
        return _(
            "You are including the statement\n\n"
            "    `{newline}`\n\n"
            "indicating that `{name}` is a variable defined outside a function.\n"
            "You are also using the same `{name}` as an argument for that\n"
            "function, thus indicating that it should be variable known only\n"
            "inside that function, which is the contrary of what `global` implied.\n"
        ).format(newline=newline, name=name)


@add_python_message
def name_assigned_to_prior_global(message="", **kwargs):
    # something like: name 'p' is assigned to before global declaration
    _ = current_lang.translate
    if "is assigned to before global declaration" in message:
        name = message.split("'")[1]
        return _(
            "You assigned a value to the variable `{name}`\n"
            "before declaring it as a global variable.\n"
        ).format(name=name)


@add_python_message
def name_used_prior_global(message="", **kwargs):
    # something like: name 'p' is used prior to global declaration
    _ = current_lang.translate
    if "is used prior to global declaration" in message:
        name = message.split("'")[1]
        return _(
            "You used the variable `{name}`\n"
            "before declaring it as a global variable.\n"
        ).format(name=name)


@add_python_message
def name_assigned_to_prior_nonlocal(message="", **kwargs):
    # something like: name 'p' is assigned to before global declaration
    _ = current_lang.translate
    if "is assigned to before nonlocal declaration" in message:
        name = message.split("'")[1]
        return _(
            "You assigned a value to the variable `{name}`\n"
            "before declaring it as a nonlocal variable.\n"
        ).format(name=name)


@add_python_message
def name_is_parameter_and_nonlocal(message="", **kwargs):
    _ = current_lang.translate
    if "is parameter and nonlocal" in message:
        name = message.split("'")[1]
        return _(
            "You used `{name}` as a parameter for a function\n"
            "before declaring it also as a nonlocal variable:\n"
            "`{name}` cannot be both at the same time.\n"
        ).format(name=name)


@add_python_message
def name_used_prior_nonlocal(message="", **kwargs):
    # something like: name 'q' is used prior to nonlocal declaration
    _ = current_lang.translate
    if "is used prior to nonlocal declaration" in message:
        name = message.split("'")[1]
        return _(
            "You used the variable `{name}`\n"
            "before declaring it as a nonlocal variable.\n"
        ).format(name=name)


@add_python_message
def nonlocal_at_module_level(message="", **kwargs):
    _ = current_lang.translate
    if "nonlocal declaration not allowed at module level" in message:
        return _(
            "You used the nonlocal keyword at a module level.\n"
            "The nonlocal keyword refers to a variable inside a function\n"
            "given a value outside that function."
        )


@add_python_message
def no_binding_for_nonlocal(message="", line=None, **kwargs):
    _ = current_lang.translate
    if "no binding for nonlocal" in message:
        name = message.split("'")[1]
        return _(
            "You declared the variable `{name}` as being a\n"
            "nonlocal variable but it cannot be found.\n"
        ).format(name=name)


@add_python_message
def unexpected_character_after_continuation(message="", **kwargs):
    _ = current_lang.translate
    if "unexpected character after line continuation character" in message:
        return _(
            "You are using the continuation character `\\` outside of a string,\n"
            "and it is followed by some other character(s).\n"
            "I am guessing that you forgot to enclose some content in a string.\n"
            "\n"
        )


@add_python_message
def unexpected_eof_while_parsing(
    message="", source_lines=None, linenumber=None, offset=None, **kwargs
):
    # unexpected EOF while parsing
    _ = current_lang.translate
    if "unexpected EOF while parsing" not in message:
        return
    response = _(
        "Python tells us that it reached the end of the file\n"
        "and expected more content.\n\n"
    )

    additional_response = source_analyzer.look_for_missing_bracket(
        source_lines=source_lines, max_linenumber=linenumber, offset=offset
    )

    if additional_response:
        response += (
            _("I will attempt to be give a bit more information.\n\n")
            + additional_response
        )

    return response


@add_python_message
def unmatched_parenthesis(message="", linenumber=None, **kwargs):
    _ = current_lang.translate
    # Python 3.8
    if message == "unmatched ')'":
        bracket = source_analyzer.name_bracket(")")
    elif message == "unmatched ']'":
        bracket = source_analyzer.name_bracket("]")
    elif message == "unmatched '}'":
        bracket = source_analyzer.name_bracket("}")
    else:
        return
    return _(
        "The closing {bracket} on line {linenumber} does not match anything.\n"
    ).format(bracket=bracket, linenumber=linenumber)


@add_python_message
def position_argument_follows_keyword_arg(message="", **kwargs):
    _ = current_lang.translate
    if "positional argument follows keyword argument" not in message:
        return
    return _(
        "In Python, you can call functions with only positional arguments\n\n"
        "    test(1, 2, 3)\n\n"
        "or only keyword arguments\n\n"
        "    test(a=1, b=2, c=3)\n\n"
        "or a combination of the two\n\n"
        "    test(1, 2, c=3)\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )


@add_python_message
def non_default_arg_follows_default_arg(message="", **kwargs):
    _ = current_lang.translate
    if "non-default argument follows default argument" not in message:
        return
    return _(
        "In Python, you can define functions with only positional arguments\n\n"
        "    def test(a, b, c): ...\n\n"
        "or only keyword arguments\n\n"
        "    def test(a=1, b=2, c=3): ...\n\n"
        "or a combination of the two\n\n"
        "    def test(a, b, c=3): ...\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )


@add_python_message
def python2_print(message="", **kwargs):
    _ = current_lang.translate
    if not message.startswith(
        "Missing parentheses in call to 'print'. Did you mean print("
    ):
        return
    message = message[59:-2]
    return _(
        "Perhaps you need to type\n\n"
        "     print({message})\n\n"
        "In older version of Python, `print` was a keyword.\n"
        "Now, `print` is a function; you need to use parentheses to call it.\n"
    ).format(message=message)
