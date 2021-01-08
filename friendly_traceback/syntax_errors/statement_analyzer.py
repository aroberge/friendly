"""This module contains functions that are used to
   analyze a single statement which has been identified
   as containing a syntax error with the message "invalid syntax".
"""
import sys

from . import fixers
from ..my_gettext import current_lang
from .. import debug_helper

STATEMENT_ANALYZERS = []


def add_statement_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single statement."""
    STATEMENT_ANALYZERS.append(func)

    def wrapper(statement):
        return func(statement)

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

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "==")
    if not fixers.check_statement(new_statement):
        # TODO: find a way to confirm that new error is later.
        debug_helper.log("Fix did not work in assign_instead_of_equal")
        additional_cause = _(
            "However, there might be some other errors in this statement.\n"
        )
    else:
        additional_cause = ""

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

    return cause + additional_cause, hint


@add_statement_analyzer
def print_as_statement(statement):
    _ = current_lang.translate
    cause = hint = None

    if statement.prev_token != "print":
        return cause, hint

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

    new_statement = fixers.replace_token(statement.tokens, statement.prev_token, ",")
    if fixers.check_statement(new_statement):
        cause += _("Perhaps you need to replace the dot by a comma.\n")
        return cause, hint

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


@add_statement_analyzer
def missing_colon(statement):
    """look for missing colon at the end of statement"""
    _ = current_lang.translate
    cause = hint = None

    if statement.last_token == ":" or statement.bad_token != statement.last_token:
        return cause, hint

    name = statement.first_token
    if name.is_not_in(
        [
            "class",
            "def",
            "if",
            "elif",
            "else",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
        ]
    ):
        return cause, hint

    new_statement = fixers.modify_token(
        statement.tokens, statement.bad_token, append=":"
    )
    if not fixers.check_statement(new_statement):
        return cause, hint

    name = statement.first_token

    forgot_a_colon = _("Did you forget a colon `:`?\n")

    if name.is_in(["for", "while"]):
        cause = _(
            "You wrote a `{for_while}` loop but\n"
            "forgot to add a colon `:` at the end\n"
            "\n"
        ).format(for_while=name)
        hint = forgot_a_colon
    elif name.is_in(["def", "elif", "else", "except", "finally", "if", "try", "with"]):
        cause = _(
            "You wrote a statement beginning with\n"
            "`{name}` but forgot to add a colon `:` at the end\n"
            "\n"
        ).format(name=name)
        hint = forgot_a_colon

    return cause, hint


@add_statement_analyzer
def invalid_hexadecimal(statement):
    """Identifies problem caused by invalid character in an hexadecimal number."""
    _ = current_lang.translate
    cause = hint = None

    prev = statement.prev_token
    wrong = statement.bad_token
    if not (prev.immediately_before(wrong) and prev.string.lower().startswith("0x")):
        return cause, hint

    hint = _("Did you made a mistake in writing an hexadecimal integer?\n")
    cause = _(
        "It looks like you used an invalid character (`{character}`) in an hexadecimal number.\n\n"
        "Hexadecimal numbers are base 16 integers that use the symbols `0` to `9`\n"
        "to represent values 0 to 9, and the letters `a` to `f` (or `A` to `F`)\n"
        "to represent values 10 to 15.\n"
        "In Python, hexadecimal numbers start with either `0x` or `0X`,\n"
        "followed by the characters used to represent the value of that integer.\n"
    ).format(character=wrong.string[0])
    return cause, hint


@add_statement_analyzer
def invalid_octal(statement):
    """Identifies problem caused by invalid character in an octal number."""
    _ = current_lang.translate
    cause = hint = None

    prev = statement.prev_token
    wrong = statement.bad_token
    if not (prev.immediately_before(wrong) and prev.string.lower().startswith("0o")):
        return cause, hint

    hint = _("Did you made a mistake in writing an octal integer?\n")
    cause = _(
        "It looks like you used an invalid character (`{character}`) in an octal number.\n\n"
        "Octal numbers are base 8 integers that only use the symbols `0` to `7`\n"
        "to represent values.\n"
        "In Python, hexadecimal numbers start with either `0o` or `0O`,\n"
        "(the digit zero followed by the letter `o`)\n"
        "followed by the characters used to represent the value of that integer.\n"
    ).format(character=wrong.string[0])
    return cause, hint


@add_statement_analyzer
def invalid_name(statement):
    """Identifies invalid identifiers when a name begins with a number"""
    _ = current_lang.translate
    cause = hint = None

    first = statement.prev_token
    second = statement.bad_token

    if not (first.is_number() and second.is_name() and first.end == second.start):
        return cause, hint

    cause = _("Valid names cannot begin with a number.\n")
    if first == statement.first_token:  # statement begins with this invalid identifier
        hint = cause
        return cause, hint

    if second == "i" and not first.is_complex():
        hint = _("Did you mean `{number}j`?\n").format(number=first)
        cause += _(
            "Perhaps you thought that `i` could be used to represent\n"
            "the square root of `-1`. In Python, the symbol used for this is `j`\n"
            "and the complex part is written as `some_number` immediately\n"
            "followed by `j`, with no spaces in between.\n"
            "Perhaps you meant to write `{number}j`.\n"
        ).format(number=first)
        return cause, hint

    if first.is_complex():
        note = _("[Note: `{first}` is a complex number.]\n").format(first=first)
        second.string = first.string[-1] + second.string
        first.string = first.string[:-1]
    else:
        note = ""

    hint = _(
        "Perhaps you forgot a multiplication operator, `{first} * {second}`.\n"
    ).format(first=first, second=second)
    cause = cause + hint

    if note is not None:
        cause += "\n" + note
    return cause, hint


@add_statement_analyzer
def debug_fstring(statement):
    """Detect debug feature of f-string introduced in Python 3.8"""
    _ = current_lang.translate
    cause = hint = None
    if sys.version_info >= (3, 8) or not statement.fstring_error:
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
def general_fstring_problem(statement=None):
    # General f-string problems are outside of our main priorities.
    _ = current_lang.translate
    cause = hint = None
    if not statement.fstring_error:
        return cause, hint

    cause = _(
        "The content of your f-string is invalid. Please consult the documentation:\n"
        "https://docs.python.org/3/reference/lexical_analysis.html#f-strings\n"
    )
    return cause, hint


@add_statement_analyzer
def malformed_def_missing_parens(statement):
    # Something like
    # def test: ...
    _ = current_lang.translate
    cause = hint = None

    if statement.first_token != "def":
        return cause, hint

    # TODO: remove requirement of only three tokens to be able to handle
    # something like
    # def test: something_valid  # all on one line
    #

    if (
        statement.nb_tokens != 3
        and statement.last_token != ":"
        and statement.bad_token != statement.last_token
    ):
        return cause, hint

    new_statement = fixers.modify_token(
        statement.tokens, statement.bad_token, prepend="()"
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget parentheses?\n")
        cause = _(
            "Perhaps you forgot to include parentheses.\n"
            "You might have meant to write `{line}`\n"
        ).format(line=new_statement)
        return cause, hint

    return cause, hint
