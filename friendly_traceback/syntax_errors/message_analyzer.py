"""message_analyser.py

Collection of functions that examine SyntaxError messages and
return relevant information to users.
"""
import __future__
import ast
import re
import sys

from . import syntax_utils
from . import statement_analyzer
from .. import utils
from ..my_gettext import current_lang

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
    "‛",
    "‘",
    "❛",
    "❜",
    "❟",
]


def analyze_message(message="", statement=None):
    for case in MESSAGE_ANALYZERS:
        cause = case(message=message, statement=statement)
        if cause:
            return cause
    return {}


def add_python_message(func):
    """A simple decorator that adds a function the the list of functions
    that process a message given by Python.
    """
    MESSAGE_ANALYZERS.append(func)

    def wrapper(**_kwargs):
        return func(**_kwargs)

    return wrapper


@add_python_message
def assign_to_keyword(message="", statement=None):
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
        return {}

    word = statement.bad_token
    hint = _("You cannot assign a value to `{keyword}`.").format(keyword=word)
    if word in ["None", "True", "False", "__debug__", "Ellipsis (...)"]:
        cause = _(
            "`{keyword}` is a constant in Python; you cannot assign it a value.\n" "\n"
        ).format(keyword=word)
    else:
        cause = _(
            "You were trying to assign a value to the Python keyword `{keyword}`.\n"
            "This is not allowed.\n"
            "\n"
        ).format(keyword=word)
    return {"cause": cause, "suggest": hint}


@add_python_message
def assign_to_conditional_expression(message="", **_kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to conditional expression"  # Python 3.6, 3.7
        or message == "cannot assign to conditional expression"  # Python 3.8
    ):
        hint = _("You can only assign objects to identifiers (variable names).\n")
        cause = _(
            "On the left-hand side of an equal sign, you have a\n"
            "conditional expression instead of the name of a variable.\n"
            "A conditional expression has the following form:\n\n"
            "    variable = object if condition else other_object"
        )
        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def assign_to_function_call(message="", statement=None):
    _ = current_lang.translate
    if (
        message != "can't assign to function call"  # Python 3.6, 3.7
        and message != "cannot assign to function call"  # Python 3.8
    ):
        return {}

    hint = _("You can only assign objects to identifiers (variable names).\n")

    fn_call = statement.bad_token.string + "(...)"
    line = statement.bad_line

    if line.count("=") != 1 or line.count("(") != line.count(")"):
        # we have something like  fn(a=1) = 2
        # or fn(a) = 1 = 2, etc., and we cannot determine what is a function
        # argument and what is the value assigned
        value = _("some value")
        cause = _(
            "You wrote an expression like\n\n"
            "    {fn_call} = {value}\n\n"
            "where `{fn_call}`, on the left-hand side of the equal sign, is\n"
            "a function call and not the name of a variable.\n"
        ).format(fn_call=fn_call, value=value)

        return {"cause": cause, "suggest": hint}

    info = line.split("=")
    fn_call = info[0].strip()
    value = info[1].strip()
    cause = _(
        "You wrote the expression\n\n"
        "    {fn_call} = {value}\n\n"
        "where `{fn_call}`, on the left-hand side of the equal sign, either is\n"
        "or includes a function call and is not simply the name of a variable.\n"
    ).format(fn_call=fn_call, value=value)
    return {"cause": cause, "suggest": hint}


@add_python_message
def assign_to_generator_expression(message="", **_kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to generator expression"  # Python 3.6, 3.7
        or message == "cannot assign to generator expression"  # Python 3.8
    ):
        hint = _("You can only assign objects to identifiers (variable names).\n")
        cause = _(
            "On the left-hand side of an equal sign, you have a\n"
            "generator expression instead of the name of a variable.\n"
        )
        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def assign_to_f_expression(message="", statement=None):
    _ = current_lang.translate

    if message == "cannot assign to f-string expression":
        hint = _("You can only assign objects to identifiers (variable names).\n")
        cause = _(
            "You wrote an expression that has the f-string `{fstring}`\n"
            "on the left-hand side of the equal sign.\n"
            "An f-string should only appear on the right-hand "
            "side of an equal sign.\n"
        ).format(fstring=statement.bad_token)
        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def f_string_backslash(message="", **_kwargs):
    _ = current_lang.translate
    if message != "f-string expression part cannot include a backslash":
        return {}

    cause = _(
        "You have written an f-string whose content `{...}`\n"
        "includes a backslash; this is not allowed.\n"
        "Perhaps you can replace the part that contains a backslash by\n"
        "some variable. For example, suppose that you have an f-string like:\n\n"
        "    f\"{... 'hello\\n' ...}\"\n\n"
        "you could write this as\n\n"
        "    hello = 'hello\\n'\n"
        '    f"{... hello ...}"\n'
    )
    return {"cause": cause}


def what_kind_of_literal(literal):
    _ = current_lang.translate

    try:
        a = ast.literal_eval(literal)
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
def annotated_name_cannot_be_global(message="", **_kwargs):
    # annotated name 'x' can't be global
    _ = current_lang.translate
    pattern1 = re.compile(r"annotated name '(.)' can't be global")
    match = re.search(pattern1, message)
    if not match:
        return {}
    cause = _(
        "The object named `{name}` is defined with type annotation\n"
        "as a local variable. It cannot be declared to be a global variable.\n"
    ).format(name=match.group(1))

    return {"cause": cause}


@add_python_message
def assign_to_literal(message="", statement=None):
    _ = current_lang.translate
    if (
        message == "can't assign to literal"  # Python 3.6, 3.7
        or message == "cannot assign to literal"  # Python 3.8
        or message == "cannot assign to set display"  # Python 3.8
        or message == "cannot assign to dict display"  # Python 3.8
    ):
        line = statement.bad_line.rstrip()
        info = line.split("=")
        if len(info) == 2:
            literal = info[0].strip()
            name = info[1].strip()
            if sys.version_info < (3, 8) and (
                literal.startswith("f'{") or literal.startswith('f"{')
            ):
                cause = _(
                    "You wrote an expression that has the f-string `{fstring}`\n"
                    "on the left-hand side of the equal sign.\n"
                    "An f-string should only appear on the right-hand "
                    "side of the equal sign.\n"
                ).format(fstring=statement.bad_token)
                return {"cause": cause}
        else:
            literal = None
            name = _("variable_name")

        if len(info) == 2 and name.isidentifier():
            # fmt: off
            suggest = _(
                "Perhaps you meant to write:\n\n"
                "    {name} = {literal}\n"
                "\n"
            ).format(literal=literal, name=name)
            hint = _(
                "Perhaps you meant to write `{name} = {literal}`"
            ).format(literal=literal, name=name)
            # fmt: on
        else:
            suggest = "\n"
            hint = _("You can only assign objects to identifiers (variable names).\n")

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

        cause = (
            _(
                "You wrote an expression like\n\n"
                "    {literal} = {name}\n"
                "where `{literal}`, on the left-hand side of the equal sign,\n"
                "is or includes an actual object {of_type}\n"
                "and is not simply the name of a variable.\n"
            ).format(literal=literal, name=name, of_type=of_type)
            + suggest
        )
        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def assign_to_operator(message="", statement=None):
    _ = current_lang.translate
    line = statement.bad_line.rstrip()
    if (
        message == "can't assign to operator"  # Python 3.6, 3.7
        or message == "cannot assign to operator"  # Python 3.8
    ):
        cause = _(
            "You wrote an expression that includes some mathematical operations\n"
            "on the left-hand side of the equal sign which should be\n"
            "only used to assign a value to a variable.\n"
        )
        name = could_be_identifier(line)
        if name:
            hint = _("Did you mean `{name}`?\n").format(name=name)
            cause += _(
                "Perhaps you meant to write `{name}` instead of `{original}`\n"
            ).format(name=name, original=name.replace("_", "-"))
            return {"cause": cause, "suggest": hint}
        else:
            hint = _("You can only assign objects to identifiers (variable names).\n")
            return {"cause": cause, "suggest": hint}

    return {}


def could_be_identifier(line):
    try:
        if "=" in line and "-" in line:
            lhs, *rhs = line.split("=")
            if "-" in lhs:
                lhs = lhs.replace("-", "_").strip()
                if lhs.isidentifier():
                    return lhs
        return ""
    except Exception:
        print("exception raised")
        return ""


@add_python_message
def both_nonlocal_and_global(message="", statement=None):
    _ = current_lang.translate
    if "is nonlocal and global" in message:
        cause = _(
            "You declared `{name}` as being both a global and nonlocal variable.\n"
            "A variable can be global, or nonlocal, but not both at the same time.\n"
        ).format(name=statement.next_token)
        return {"cause": cause}
    return {}


@add_python_message
def break_outside_loop(message="", **_kwargs):
    _ = current_lang.translate

    if "'break' outside loop" in message:
        cause = _(
            "The Python keyword `break` can only be used "
            "inside a `for` loop or inside a `while` loop.\n"
        )
        return {"cause": cause}
    return {}


@add_python_message
def continue_outside_loop(message="", **_kwargs):
    _ = current_lang.translate
    if "'continue' not properly in loop" in message:
        cause = _(
            "The Python keyword `continue` can only be used "
            "inside a `for` loop or inside a `while` loop.\n"
        )
        return {"cause": cause}
    return {}


@add_python_message
def delete_function_call(message="", statement=None):
    _ = current_lang.translate
    if (
        message == "can't delete function call"  # Python 3.6, 3.7
        or message == "cannot delete function call"  # Python 3.8
    ):
        line = statement.bad_line.rstrip()
        correct = "del {name}".format(name=statement.bad_token)
        cause = _(
            "You attempted to delete a function call\n\n"
            "    {line}\n"
            "instead of deleting the function's name\n\n"
            "    {correct}\n"
        ).format(line=line, correct=correct)
        return {"cause": cause}
    return {}


@add_python_message
def delete_x(message="", statement=None):
    _ = current_lang.translate
    if not (
        message == "can't delete keyword"  # Python 3.6, 3.7
        or message == "can't delete literal"
        or message == "cannot delete literal"  # Python 3.8
        or message == "cannot delete None"
        or message == "cannot delete True"
        or message == "cannot delete False"
    ):
        return {}

    if statement.bad_token.is_in(["None", "True", "False"]):
        cause = _("You cannot delete the constant `{constant}`.\n").format(
            constant=statement.bad_token
        )
    else:
        cause = _(
            "You cannot delete the literal `{literal}`.\n"
            "You can only delete the names of objects, or\n"
            "individual items in a container.\n"
        ).format(literal=statement.bad_token)
    return {"cause": cause}


@add_python_message
def duplicate_argument_in_function_definition(message="", **_kwargs):
    _ = current_lang.translate
    if "duplicate argument" in message and "function definition" in message:
        name = message.split("'")[1]
        cause = _(
            "You have defined a function repeating the keyword argument\n\n"
            "    {name}\n"
            "twice; each keyword argument should appear only once"
            " in a function definition.\n"
        ).format(name=name)
        return {"cause": cause}
    return {}


@add_python_message
def eol_while_scanning_string_literal(message="", statement=None):
    _ = current_lang.translate
    if (
        "EOL while scanning string literal" in message
        or "unterminated string literal" in message  # Python 3.10
    ):
        hint = _("Did you forget a closing quote?\n")
        cause = _(
            "You starting writing a string with a single or double quote\n"
            "but never ended the string with another quote on that line.\n"
        )
        # second if case for Python 3.10
        if statement.prev_token == "\\" or statement.bad_line[-2] == "\\":
            cause += _(
                "Perhaps you meant to write the backslash character, `\\`\n"
                "as the last character in the string and forgot that you\n"
                "needed to escape it by writing two `\\` in a row.\n"
            )
            hint = _("Did you forget to escape a backslash character?\n")

        return {"cause": cause, "suggest": hint}
    return {}


@add_python_message
def expression_cannot_contain_assignment(message="", **_kwargs):
    _ = current_lang.translate
    if "expression cannot contain assignment, perhaps you meant" not in message:
        return {}
    cause = _(
        "One of the following two possibilities could be the cause:\n\n"
        "(1) You meant to do a comparison with == and wrote = instead.\n\n"
        "(2) You called a function with a named argument:\n\n"
        "    a_function(invalid=...)\n\n"
        "where `invalid` is not a valid identifier (variable name) in Python\n"
        "either because it starts with a number, or is a string,\n"
        "or contains a period, etc.\n"
        "\n"
    )
    return {"cause": cause}


@add_python_message
def generator_expression_must_be_parenthesized(message="", **_kwargs):
    _ = current_lang.translate
    if "Generator expression must be parenthesized" not in message:
        return {}
    cause = _(
        "You are using a generator expression, something of the form\n"
        "    `x for x in thing`\n"
        "You must add parentheses enclosing that expression.\n"
    )
    return {"cause": cause}


@add_python_message
def keyword_argument_repeated(message="", statement=None):
    _ = current_lang.translate
    if "keyword argument repeated" not in message:
        return {}
    cause = _(
        "You have called a function repeating the same keyword argument (`{arg}`).\n"
        "Each keyword argument should appear only once in a function call.\n"
    ).format(arg=statement.bad_token)
    return {"cause": cause}


@add_python_message
def keyword_cannot_be_expression(message="", **_kwargs):
    _ = current_lang.translate
    if "keyword can't be an expression" not in message:
        return {}
    cause = _(
        "You likely called a function with a named argument:\n\n"
        "   `a_function(invalid=something)`\n\n"
        "where `invalid` is not a valid variable name in Python\n"
        "either because it starts with a number, or is a string,\n"
        "or contains a period, etc.\n"
        "\n"
    )
    return {"cause": cause}


@add_python_message
def invalid_character_in_identifier(message="", statement=None):
    _ = current_lang.translate
    copy_paste = _("Did you use copy-paste?\n")
    if "invalid character" not in message:
        return {}

    bad_character = statement.bad_token
    python_says = _(
        "Python indicates that you used the unicode character"
        " `{bad_character}`\n"
        "which is not allowed.\n"
    ).format(bad_character=bad_character)

    if bad_character in bad_quotation_marks:
        hint = _("Did you mean to use a normal quote character, `'` or `\"`?\n")
        cause = (
            copy_paste
            + python_says
            + _(
                "I suspect that you used a fancy unicode quotation mark\n"
                "instead of a normal single or double quote for a string."
                "\n"
            )
        )
        return {"cause": cause, "suggest": hint}

    return {"cause": python_says}


@add_python_message
def mismatched_parenthesis(message="", statement=None):
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
            return {}
    else:
        lineno = match.group(3)

    opening = match.group(2)
    closing = match.group(1)

    if lineno is not None:
        cause = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}` on line {lineno}.\n\n"
        ).format(closing=closing, opening=opening, lineno=lineno)
    else:
        cause = _(
            "Python tells us that the closing `{closing}` on the last line shown\n"
            "does not match the opening `{opening}`.\n\n"
        ).format(closing=closing, opening=opening)

    additional_cause = statement_analyzer.mismatched_brackets(statement)

    if additional_cause:
        cause += (
            _("I will attempt to be give a bit more information.\n\n")
            + additional_cause["cause"]
        )

    return {"cause": cause}


@add_python_message
def unterminated_f_string(message="", statement=None):
    _ = current_lang.translate
    if "f-string: unterminated string" not in message:
        return {}

    hint = _("Perhaps you forgot a closing quote.\n")
    cause = _(
        "Inside the f-string `{fstring}`, \n"
        "you have another string, which starts with either a\n"
        "single quote (') or double quote (\"), without a matching closing one.\n"
    ).format(fstring=statement.bad_token)
    return {"cause": cause, "suggest": hint}


@add_python_message
def name_is_parameter_and_global(message="", statement=None):
    # something like: name 'x' is parameter and global
    _ = current_lang.translate
    line = statement.statement
    if "is parameter and global" not in message:
        return {}

    name = message.split("'")[1]
    if name in line and "global" in line:
        newline = line
    else:
        newline = f"global {name}"
    cause = _(
        "You are including the statement\n\n"
        "    {newline}\n\n"
        "indicating that `{name}` is a variable defined outside a function.\n"
        "You are also using the same `{name}` as an argument for that\n"
        "function, thus indicating that it should be variable known only\n"
        "inside that function, which is the contrary of what `global` implied.\n"
    ).format(newline=newline, name=name)
    return {"cause": cause}


@add_python_message
def name_assigned_to_prior_global(message="", **_kwargs):
    # something like: name 'p' is assigned to before global declaration
    _ = current_lang.translate
    if "is assigned to before global declaration" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You assigned a value to the variable `{name}`\n"
        "before declaring it as a global variable.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_used_prior_global(message="", **_kwargs):
    # something like: name 'p' is used prior to global declaration
    _ = current_lang.translate
    if "is used prior to global declaration" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You used the variable `{name}`\n" "before declaring it as a global variable.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_assigned_to_prior_nonlocal(message="", **_kwargs):
    # something like: name 'p' is assigned to before global declaration
    _ = current_lang.translate
    if "is assigned to before nonlocal declaration" not in message:
        return {}

    name = message.split("'")[1]
    hint = _("Did you forget to add `nonlocal`?\n")
    cause = _(
        "You assigned a value to the variable `{name}`\n"
        "before declaring it as a nonlocal variable.\n"
    ).format(name=name)
    return {"cause": cause, "suggest": hint}


@add_python_message
def name_is_parameter_and_nonlocal(message="", **_kwargs):
    _ = current_lang.translate
    if "is parameter and nonlocal" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You used `{name}` as a parameter for a function\n"
        "before declaring it also as a nonlocal variable:\n"
        "`{name}` cannot be both at the same time.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def name_used_prior_nonlocal(message="", **_kwargs):
    # something like: name 'q' is used prior to nonlocal declaration
    _ = current_lang.translate
    if "is used prior to nonlocal declaration" not in message:
        return {}

    hint = _("Did you forget to write `nonlocal` first?\n")
    name = message.split("'")[1]
    cause = _(
        "You used the variable `{name}`\n"
        "before declaring it as a nonlocal variable.\n"
    ).format(name=name)
    return {"cause": cause, "suggest": hint}


@add_python_message
def nonlocal_at_module_level(message="", **_kwargs):
    _ = current_lang.translate
    if "nonlocal declaration not allowed at module level" not in message:
        return {}
    cause = _(
        "You used the nonlocal keyword at a module level.\n"
        "The nonlocal keyword refers to a variable inside a function\n"
        "given a value outside that function."
    )
    return {"cause": cause}


@add_python_message
def no_binding_for_nonlocal(message="", **_kwargs):
    _ = current_lang.translate
    if "no binding for nonlocal" not in message:
        return {}

    name = message.split("'")[1]
    cause = _(
        "You declared the variable `{name}` as being a\n"
        "nonlocal variable but it cannot be found.\n"
    ).format(name=name)
    return {"cause": cause}


@add_python_message
def unexpected_character_after_continuation(message="", **_kwargs):
    _ = current_lang.translate
    if "unexpected character after line continuation character" not in message:
        return {}

    cause = _(
        "You are using the continuation character `\\` outside of a string,\n"
        "and it is followed by some other character(s).\n"
        "I am guessing that you forgot to enclose some content in a string.\n"
        "\n"
    )
    return {"cause": cause}


@add_python_message
def unexpected_eof_while_parsing(message="", statement=None):
    # unexpected EOF while parsing
    _ = current_lang.translate
    if "unexpected EOF while parsing" not in message:
        return {}

    cause = _(
        "Python tells us that it reached the end of the file\n"
        "and expected more content.\n\n"
    )
    additional_cause = statement_analyzer.unclosed_bracket(statement)
    if additional_cause:
        cause += (
            _("I will attempt to be give a bit more information.\n\n")
            + additional_cause["cause"]
        )
    return {"cause": cause}


@add_python_message
def unmatched_parenthesis(message="", statement=None):
    _ = current_lang.translate
    # Python 3.8
    if message == "unmatched ')'":
        bracket = syntax_utils.name_bracket(")")
    elif message == "unmatched ']'":
        bracket = syntax_utils.name_bracket("]")
    elif message == "unmatched '}'":
        bracket = syntax_utils.name_bracket("}")
    else:
        return {}
    cause = _(
        "The closing {bracket} on line {linenumber} does not match anything.\n"
    ).format(bracket=bracket, linenumber=statement.linenumber)
    return {"cause": cause}


@add_python_message
def position_argument_follows_keyword_arg(message="", **_kwargs):
    _ = current_lang.translate
    if "positional argument follows keyword argument" not in message:
        return {}
    cause = _(
        "In Python, you can call functions with only positional arguments\n\n"
        "    test(1, 2, 3)\n\n"
        "or only keyword arguments\n\n"
        "    test(a=1, b=2, c=3)\n\n"
        "or a combination of the two\n\n"
        "    test(1, 2, c=3)\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )
    return {"cause": cause}


@add_python_message
def non_default_arg_follows_default_arg(message="", **_kwargs):
    _ = current_lang.translate
    if "non-default argument follows default argument" not in message:
        return {}
    cause = _(
        "In Python, you can define functions with only positional arguments\n\n"
        "    def test(a, b, c): ...\n\n"
        "or only keyword arguments\n\n"
        "    def test(a=1, b=2, c=3): ...\n\n"
        "or a combination of the two\n\n"
        "    def test(a, b, c=3): ...\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )
    return {"cause": cause}


@add_python_message
def python2_print(message="", **_kwargs):
    _ = current_lang.translate
    if not message.startswith(
        "Missing parentheses in call to 'print'. Did you mean print("
    ):
        return {}
    message = message[59:-2]
    if len(message) > 40:
        message = message[0:15] + " ... "
    cause = _(
        "Perhaps you need to type\n\n"
        "     print({message})\n\n"
        "In older version of Python, `print` was a keyword.\n"
        "Now, `print` is a function; you need to use parentheses to call it.\n"
    ).format(message=message)
    hint = _("Did you mean `print({message})`?\n").format(message=message)
    return {"cause": cause, "suggest": hint}


@add_python_message
def cannot_use_starred_expression(message="", **_kwargs):
    _ = current_lang.translate
    if not message == "can't use starred expression here":
        return {}

    cause = _(
        "The star operator `*` is interpreted to mean that\n"
        "iterable unpacking is to be used to assign a name\n"
        "to each item of an iterable, which does not make sense here.\n"
    )

    return {"cause": cause}


@add_python_message
def return_outside_function(message="", **_kwargs):
    _ = current_lang.translate
    if not message == "'return' outside function":
        return {}

    cause = _("You can only use a `return` statement inside a function or method.\n")
    return {"cause": cause}


@add_python_message
def too_many_nested_blocks(message="", **_kwargs):
    _ = current_lang.translate
    if not message == "too many statically nested blocks":
        return {}

    hint = _("Seriously?\n")
    cause = _(
        "You cannot be serious!\n\n"
        "In case this is a mistake in a real program, please\n"
        "consider reducing the number of nested code blocks.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_python_message
def named_arguments_must_follow_bare_star(message="", **_kwargs):
    _ = current_lang.translate
    if not message == "named arguments must follow bare *":
        return {}

    hint = _("Did you forget something after `*`?\n")
    cause = _(
        "Assuming you were defining a function, you need\n"
        "to replace `*` by either `*arguments` or\n"
        "by `*, named_argument=value`.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_python_message
def you_found_it(message="", **_kwargs):
    _ = current_lang.translate
    if not message == "You found it!":
        return {}

    cause = _(
        "This is a message that was added in Python 3.9\n"
        "to prevent redefining `__peg_parser__`.\n"
        "It should not be present in other versions.\n"
    )
    return {"cause": cause}


@add_python_message
def from__future__not_defined(message="", **_kwargs):
    _ = current_lang.translate
    pattern = re.compile(r"future feature (.*) is not defined")
    match = re.search(pattern, message)
    if match is None:
        return {}

    names = __future__.all_feature_names
    available = _("The available features are `{names}`.\n").format(
        names=utils.list_to_string(names)
    )
    feature = match.group(1)
    if feature == "*":
        cause = _(
            "When using a `from __future__ import` statement,\n"
            "you must import specific named features.\n"
        )
        cause += "\n" + available
        return {"cause": cause}

    else:
        names = __future__.all_feature_names
        similar = utils.get_similar_words(feature, names)
        if similar:
            hint = _("Did you mean `{name}`?\n").format(name=similar[0])
            cause = _(
                "Instead of `{feature}`, perhaps you meant to import `{name}`.\n"
            ).format(feature=feature, name=similar[0])
            return {"cause": cause, "suggest": hint}
        else:
            cause = _(
                "`{feature}` is not a valid feature of module `__future__`.\n"
            ).format(feature=feature)
            cause += "\n" + available
            return {"cause": cause}


@add_python_message
def from__future__at_begin(message="", **_kwargs):
    _ = current_lang.translate
    if message != "from __future__ imports must occur at the beginning of the file":
        return {}

    cause = _(
        "A `from __future__ import` statement changes the way Python\n"
        "interprets the code in a file.\n"
        "It must appear at the beginning of the file."
    )
    return {"cause": cause}


@add_python_message
def import_braces(message="", **_kwargs):
    _ = current_lang.translate
    if message != "not a chance":
        return {}

    cause = _(
        "I suspect you wrote `from __future__ import braces` following\n"
        "someone else's suggestion. This will never work.\n\n"
        "Unlike other programming languages, Python's code block are defined by\n"
        "their indentation level, and not by using some curly braces, like `{...}`.\n"
    )
    return {"cause": cause}


@add_python_message
def invalid_octal(message="", statement=None):
    # Before Python 3.8, we'd only get "invalid syntax"
    if "in octal literal" not in message:
        return {}

    return statement_analyzer.invalid_octal(statement)


@add_python_message
def eof_unclosed_triple_quoted(message="", **_kwargs):
    _ = current_lang.translate
    if not (
        message == "EOF while scanning triple-quoted string literal"
        or "unterminated triple-quoted string literal" in message
    ):
        return {}

    cause = _(
        "You started writing a triple-quoted string but never wrote\n"
        "the triple quotes needed to end the string.\n"
    )

    return {"cause": cause}


def proper_decimal_or_octal_number(prev_str, bad_str):
    # see next two cases
    _ = current_lang.translate
    if not (set(prev_str).issubset("_0") and prev_str.startswith("0")):  # noqa
        return {}

    if prev_str == "0" and set(bad_str).issubset("01234567_"):
        correct = "0o" + bad_str
        hint = _("Did you mean `{num}`?\n").format(num=correct)
        cause = _(
            "Perhaps you meant to write the octal number `{num}`\n"
            "and forgot the letter 'o', or perhaps you meant to write\n"
            "a decimal integer and did not know that it could not start with zeros.\n"
        ).format(num=correct)
        return {"cause": cause, "suggest": hint}
    elif set(bad_str).issubset("0123456789_"):
        correct = bad_str.lstrip("_")
        hint = _("Did you mean `{num}`?\n").format(num=correct)
        cause = _(
            "Perhaps you meant to write the integer `{num}`\n"
            "and did not know that it could not start with zeros.\n"
        ).format(num=correct)
        return {"cause": cause, "suggest": hint}

    return {}


@add_python_message
def invalid_token(message="", statement=None):
    # Seen this for Python 3.6, 3.7 for would-be decimal number starting with zero.
    _ = current_lang.translate
    if not (message == "invalid token"):
        return {}

    prev_str = statement.prev_token.string
    bad_str = statement.bad_token.string
    return proper_decimal_or_octal_number(prev_str, bad_str)


@add_python_message
def leading_zeros_in_decimal_integers(message="", statement=None):
    # Same as previous case but for Python 3.8+
    _ = current_lang.translate
    if not (
        message.startswith(
            "leading zeros in decimal integer literals are not permitted"
        )
    ):
        return {}

    prev_str = statement.prev_token.string
    bad_str = statement.bad_token.string
    return proper_decimal_or_octal_number(prev_str, bad_str)


@add_python_message
def forgot_paren_around_comprehension(message="", **_kwargs):
    # Python 3.10+
    _ = current_lang.translate
    if not message == "did you forget parentheses around the comprehension target?":
        return {}

    # message same as from statement_analyzer.comprehension_condition_or_tuple

    cause_tuple = _(
        "I am guessing that you were writing a comprehension or a generator expression\n"
        "and forgot to include parentheses around tuples.\n"
        "As an example, instead of writing\n\n"
        "    [i, i**2 for i in range(10)]\n\n"
        "you would need to write\n\n"
        "    [(i, i**2) for i in range(10)]\n\n"
    )
    hint = _("Did you forget parentheses?\n")
    return {"cause": cause_tuple, "suggest": hint}


# # --------- Keep this last
# @add_python_message
# def general_fstring_problem(message="", statement=None):
#     # General f-string problems are outside of our main priorities.
#     _ = current_lang.translate
#     cause = hint = None
#     if not statement.fstring_error:
#         return cause, hint
#
#     cause = _(
#         "The content of your f-string is invalid. Please consult the documentation:\n"
#         "https://docs.python.org/3/reference/lexical_analysis.html#f-strings\n"
#     )
#     return cause, hint
