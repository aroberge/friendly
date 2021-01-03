"""This module contains functions that are used to
   analyze a single statement which has been identified
   as containing a syntax error with the message "invalid syntax".
"""
import sys

from ..my_gettext import current_lang
from .. import debug_helper

STATEMENT_ANALYZERS = []


def add_statement_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single statement."""
    STATEMENT_ANALYZERS.append(func)

    def wrapper(tokens, offset=None):
        return func(tokens, offset=offset)

    return wrapper


# ========================================================
# Main calling function
# ========================================================


def analyze_statement(statement):
    """Analyzes the statement as identified by Python as that
    on which the error occurred."""
    if not statement.tokens:
        debug_helper.log("Statement with no tokens in statement_analyser.py")
        return None, None

    for analyzer in STATEMENT_ANALYZERS:
        cause, hint = analyzer(statement)
        if cause:
            return cause, hint
    return None, None


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order could possibly yield incorrect results
# ==================


@add_statement_analyzer
def copy_pasted_code(statement):
    """Detecting code that starts with a Python prompt"""
    _ = current_lang.translate
    cause = hint = None
    if statement.nb_tokens < 2:
        return cause, hint

    tokens = statement.tokens
    if tokens[0] == ">>" and tokens[1] == ">":
        cause = _(
            "It looks like you copy-pasted code from an interactive interpreter.\n"
            "The Python prompt, `>>>`, should not be included in your code.\n"
        )
        hint = _("Did you use copy-paste?\n")
    return cause, hint


@add_statement_analyzer
def detect_walrus(statement):
    """Detecting if code uses named assignment operator := with an
    older version of Python.
    """
    _ = current_lang.translate
    cause = hint = None
    if sys.version_info >= (3, 8):
        return cause, hint

    # Normally, the token identified as the bad token should be
    # '='; however, in some test cases where a named assignment
    # is not allowed, it is ':' that is identified as the
    # bad token.

    bad = statement.bad_token
    prev = statement.prev_token
    next_token = statement.next_token

    if (prev == ":" and bad == "=" and bad.immediately_after(prev)) or (
        bad == ":" and next_token == "=" and bad.immediately_before(next_token)
    ):
        hint = _("Your Python version does not support this f-string feature.\n")
        cause = _(
            "You appear to be using the operator `:=`, sometimes called\n"
            "the walrus operator. This operator requires the use of\n"
            "Python 3.8 or newer. You are using version {version}.\n"
        ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")

    return cause, hint


@add_statement_analyzer
def debug_fstring(statement):
    """detect debug feature of f-string introduced in Python 3.8"""
    _ = current_lang.translate
    cause = hint = None
    if sys.version_info >= (3, 8):
        return cause, hint
    if not statement.fstring_error:
        return cause, hint

    if statement.bad_token == "=" and statement.prev_token.is_identifier():
        if statement.next_token == ")":
            hint = _("Your Python version does not support this f-string feature.\n")
            cause = _(
                "You are likely using a 'debug' syntax of f-strings introduced\n"
                "in Python version 3.8. You are using version {version}.\n"
            ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")
        else:
            cause = _(
                "You are likely trying to assign a value within an f-string.\n"
                "This is not allowed.\n"
            )
    return cause, hint


@add_statement_analyzer
def detect_backquote(statement):
    """Detecting if the error is due to using `x` which was allowed
    in Python 2.
    """
    _ = current_lang.translate
    cause = hint = None
    if statement.bad_token == "`":
        hint = _("You should not use the backquote character.\n")
        cause = _(
            "You are using the backquote character.\n"
            "Either you meant to write a single quote, ', "
            "or copied Python 2 code;\n"
            "in this latter case, use the function `repr(x)`."
        )
    return cause, hint


@add_statement_analyzer
def assign_to_a_keyword(statement):
    """Checks to see if line is of the form 'keyword = ...'"""
    _ = current_lang.translate
    cause = hint = None
    if statement.bad_token == "=" and statement.prev_token.is_keyword():
        cause = _(
            "You were trying to assign a value to the Python keyword `{keyword}`.\n"
            "This is not allowed.\n"
            "\n"
        ).format(keyword=statement.prev_token)
    return cause, hint


@add_statement_analyzer
def confused_elif(statement):
    _ = current_lang.translate
    cause = hint = None
    name = None
    if statement.bad_token == "elseif" or statement.prev_token == "elseif":
        name = "elseif"
    elif statement.bad_token == "if" and statement.prev_token == "else":
        name = "else if"
    if name:
        hint = _("Perhaps you meant to write `elif`.\n")
        cause = _(
            "You likely meant to use Python's `elif` keyword\n"
            "but wrote `{name}` instead\n"
            "\n"
        ).format(name=name)
    return cause, hint


@add_statement_analyzer
def import_from(statement):
    _ = current_lang.translate
    cause = hint = None
    if statement.bad_token != "from" or statement.tokens[0] != "import":
        return cause, hint

    function = statement.prev_token
    module = statement.next_token

    hint = _("Did you mean `from {module} import {function}`?\n").format(
        module=module, function=function
    )
    cause = _(
        "You wrote something like\n\n"
        "    import {function} from {module}\n"
        "instead of\n\n"
        "    from {module} import {function}\n\n"
        "\n"
    ).format(module=module, function=function)
    return cause, hint


@add_statement_analyzer
def keyword_as_attribute(statement):
    """Will identify something like  obj.True ..."""
    _ = current_lang.translate
    cause = hint = None
    if statement.prev_token != ".":
        return cause, hint

    word = statement.bad_token
    if word.is_keyword():
        cause = _(
            "You cannot use the Python keyword `{word}` as an attribute.\n\n"
        ).format(word=word)
    elif word == "__debug__":
        cause = _("You cannot use the constant `__debug__` as an attribute.\n\n")

    if cause is not None:
        hint = _("`{word}` cannot be used as an attribute.\n").format(word=word)

    return cause, hint


@add_statement_analyzer
def misplaced_quote(statement):
    """This looks for a misplaced quote, something like
       info = 'don't ...

    The clue we are looking for is a STRING token ('don')
    followed by something else than a string.
    """
    _ = current_lang.translate
    cause = hint = None

    if not statement.prev_token.is_string():
        return cause, hint

    bad_token = statement.bad_token
    if bad_token.is_identifier():
        bad_string = statement.prev_token.string
        for fn in [int, float, complex]:
            try:
                fn(bad_string)  # Definitely not a word!
                return cause, hint
            except Exception:
                pass

        hint = _("Perhaps you misplaced a quote.\n")
        cause = _(
            "There appears to be a Python identifier (variable name)\n"
            "immediately following a string.\n"
            "I suspect that you were trying to use a quote inside a string\n"
            "that was enclosed in quotes of the same kind.\n"
        )

    return cause, hint


@add_statement_analyzer
def assign_instead_of_equal(statement):
    """Checks to see if an assignment sign, '=', has been used instead of
    an equal sign, '==', in an if or elif statement."""
    _ = current_lang.translate
    cause = hint = None

    if not statement.bad_token == "=":
        return cause, hint

    if not statement.first_token.is_in(["if", "elif", "while"]):
        return cause, hint

    # TODO: see if we can replace = by == and get valid syntax.

    equal = _("Perhaps you needed `==` instead of `=`.\n")
    equal_or_walrus = _("Perhaps you needed `==` or `:=` instead of `=`.\n")
    if sys.version_info < (3, 8):
        cause = _(
            "You used an assignment operator `=` instead of an equality operator `==`.\n"
        )
        hint = equal
    else:
        cause = _(
            "You used an assignment operator `=`; perhaps you meant to use \n"
            "an equality operator, `==`, or the walrus operator `:=`.\n"
        )
        hint = equal_or_walrus
    return cause, hint


@add_statement_analyzer
def print_as_statement(statement):
    _ = current_lang.translate
    cause = hint = None

    if statement.prev_token != "print":
        return cause, hint

    # TODO: add hint
    # TODO: check to see if perhaps [] were used instead of ()
    if statement.bad_token != "(":
        cause = _(
            "In older version of Python, `print` was a keyword.\n"
            "Now, `print` is a function; you need to use parentheses to call it.\n"
        )
    return cause, hint


@add_statement_analyzer
def calling_pip(statement):
    _ = current_lang.translate
    cause = hint = None
    # TODO: check if we cover other cases of using Python from an interpreter.
    if not statement.first_token.is_in(["pip", "python"]):
        return cause, hint

    use_pip = _(
        "It looks as if you are attempting to use pip to install a module.\n"
        "`pip` is a command that needs to run in a terminal,\n"
        "not from a Python interpreter.\n"
    )

    for tok in statement.tokens:
        if tok == "pip":
            hint = _("Pip cannot be used in a Python interpreter.\n")
            return use_pip, hint
    return cause, hint


@add_statement_analyzer
def dot_followed_by_bracket(statement):
    _ = current_lang.translate
    cause = hint = None

    if statement.bad_token.is_in("()[]{}") and statement.prev_token == ".":
        cause = _("You cannot have a dot `.` followed by `{bracket}`.\n").format(
            bracket=statement.bad_token
        )
    # TODO: see if replacing the dot by a comma would fix the problem.
    return cause, hint


@add_statement_analyzer
def raise_single_exception(statement):
    _ = current_lang.translate
    cause = hint = None
    if statement.first_token != "raise":
        return cause, hint

    if statement.bad_token == "," and statement.prev_token.is_identifier():
        cause = _(
            "It looks like you are trying to raise an exception using Python 2 syntax.\n"
        )
    return cause, hint


@add_statement_analyzer
def invalid_double_star_operator(statement):
    _ = current_lang.translate
    cause = hint = None

    if statement.bad_token == "**":
        cause = _(
            "The double star operator `**` is likely interpreted to mean that\n"
            "dict unpacking is to be used which does not make sense here.\n"
        )

    return cause, hint
