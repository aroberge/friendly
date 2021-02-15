"""This module contains functions that are used to
   analyze a single statement which has been identified
   as containing a syntax error with the message "invalid syntax".
"""
import keyword
import sys

from . import fixers
from . import syntax_utils
from ..my_gettext import current_lang, internal_error
from .. import debug_helper
from .. import token_utils
from .. import utils

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
        return {"cause": internal_error()}

    for analyzer in STATEMENT_ANALYZERS:
        cause = analyzer(statement)
        if isinstance(cause, tuple):
            cause, hint = cause
            if cause:
                if hint:
                    return {"cause": cause, "suggest": hint}
                else:
                    return {"cause": cause}
        elif cause:
            return cause
    return {}


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order could possibly yield incorrect results
# ==================


@add_statement_analyzer
def mismatched_brackets(statement):
    """Detecting code that ends with an unmatched closing bracket"""
    _ = current_lang.translate
    if not (statement.end_bracket and statement.bad_token == statement.last_token):
        return {}

    if not statement.begin_brackets:
        lineno = statement.end_bracket.start_row
        source = f"\n    {lineno}: {statement.source_lines[lineno - 1]}"
        shift = len(str(lineno)) + statement.end_bracket.start_col + 6
        source += " " * shift + "^\n"

        cause = (
            _(
                "The closing {bracket} on line {linenumber}"
                " does not match anything.\n"
            ).format(
                bracket=syntax_utils.name_bracket(statement.end_bracket),
                linenumber=statement.end_bracket.start_row,
            )
            + source
        )

        return {"cause": cause}

    open_bracket = statement.begin_brackets[-1]
    open_lineno = open_bracket.start_row
    end_bracket = statement.end_bracket
    end_lineno = end_bracket.start_row

    source = f"\n    {open_lineno}: {statement.source_lines[open_lineno - 1]}"
    shift = len(str(open_lineno)) + open_bracket.start_col + 6
    if open_lineno == end_lineno:
        source += " " * shift + "^"
        shift = end_bracket.start_col - open_bracket.start_col - 1
        source += " " * shift + "^\n"
    else:
        source += " " * shift + "^\n"
        source += f"    {end_lineno}: {statement.source_lines[end_lineno - 1]}"
        shift = len(str(end_lineno)) + end_bracket.start_col + 6
        source += " " * shift + "^\n"

    cause = (
        _(
            "The closing {bracket} on line {close_lineno} does not match "
            "the opening {open_bracket} on line {open_lineno}.\n"
        ).format(
            bracket=syntax_utils.name_bracket(statement.end_bracket),
            close_lineno=statement.end_bracket.start_row,
            open_bracket=syntax_utils.name_bracket(open_bracket),
            open_lineno=open_bracket.start_row,
        )
        + source
    )
    return {"cause": cause}


@add_statement_analyzer
def copy_pasted_code(statement):
    """Detecting code that starts with a Python prompt"""
    _ = current_lang.translate
    if statement.nb_tokens < 2:
        return {}

    tokens = statement.tokens
    if tokens[0] == ">>" and tokens[1] == ">":
        cause = _(
            "It looks like you copy-pasted code from an interactive interpreter.\n"
            "The Python prompt, `>>>`, should not be included in your code.\n"
        )
        hint = _("Did you use copy-paste?\n")
        return {"cause": cause, "suggest": hint}
    return {}


@add_statement_analyzer
def detect_walrus(statement):
    """Detecting if code uses named assignment operator := with an
    older version of Python.
    """
    _ = current_lang.translate
    if sys.version_info >= (3, 8):
        return {}

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
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def detect_backquote(statement):
    """Detecting if the error is due to using `x` which was allowed
    in Python 2.
    """
    _ = current_lang.translate
    if statement.bad_token == "`":
        hint = _("You should not use the backquote character.\n")
        cause = _(
            "You are using the backquote character.\n"
            "Either you meant to write a single quote, ', "
            "or copied Python 2 code;\n"
            "in this latter case, use the function `repr(x)`."
        )
        return {"cause": cause, "suggest": hint}
    return {}


@add_statement_analyzer
def keyword_as_attribute(statement):
    """Will identify something like  obj.True ..."""
    _ = current_lang.translate
    if statement.prev_token != ".":
        return {}

    word = statement.bad_token
    if word.is_keyword():
        cause = _(
            "You cannot use the Python keyword `{word}` as an attribute.\n\n"
        ).format(word=word)
    elif word == "__debug__":
        cause = _("You cannot use the constant `__debug__` as an attribute.\n\n")
    else:
        return {}

    hint = _("`{word}` cannot be used as an attribute.\n").format(word=word)
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def confused_elif(statement):
    _ = current_lang.translate
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
        return {"cause": cause, "suggest": hint}
    return {}


@add_statement_analyzer
def import_from(statement):
    _ = current_lang.translate
    if statement.bad_token != "from" or statement.tokens[0] != "import":
        return {}

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
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def misplaced_quote(statement):
    """This looks for a misplaced quote, something like
       info = 'don't ...

    The clue we are looking for is a STRING token ('don')
    followed by something else than a string.
    """
    _ = current_lang.translate
    if not statement.prev_token.is_string():
        return {}

    bad_token = statement.bad_token
    if bad_token.is_identifier():
        bad_string = statement.prev_token.string
        for fn in [int, float, complex]:
            try:
                fn(bad_string)  # Definitely not a word!
                return {}
            except Exception:
                pass

        hint = _("Perhaps you misplaced a quote.\n")
        cause = _(
            "There appears to be a Python identifier (variable name)\n"
            "immediately following a string.\n"
            "I suspect that you were trying to use a quote inside a string\n"
            "that was enclosed in quotes of the same kind.\n"
        )
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def space_between_operators(statement):
    """Detect if some space has been inserted between two operators"""
    _ = current_lang.translate

    is_op = token_utils.is_operator
    if not is_op(statement.bad_token):
        return {}

    prev = statement.prev_token
    bad = statement.bad_token
    next_ = statement.next_token

    hint = _("Did you leave some spaces between operators?\n")
    possible_cause = _(
        "It looks like you wrote two operators, `{first}` and `{second}`,\n"
        "separated by spaces instead of writing them as a single operator:\n"
        "`{correct}`"
    )

    # TODO: check that this fixes the problem
    if is_op(prev) and is_op(prev.string + bad.string):
        cause = possible_cause.format(
            first=prev.string, second=bad.string, correct=prev.string + bad.string
        )
        return {"cause": cause, "suggest": hint}
    elif is_op(next_) and is_op(bad.string + next_.string):
        cause = possible_cause.format(
            first=bad.string, second=next_.string, correct=bad.string + next_.string
        )
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def inverted_comparison_operators(statement):
    """Detect if comparison operators might have been inverted"""
    _ = current_lang.translate

    is_op = token_utils.is_operator
    if not is_op(statement.bad_token):
        return {}

    prev = statement.prev_token
    bad = statement.bad_token
    next_ = statement.next_token

    hint = _("Did you write operators in an incorrect order?\n")
    possible_cause = _(
        "It looks like you wrote two operators (`{first}` and `{second}`)\n"
        "in the wrong order: `{wrong}` instead of `{correct}`.\n"
    )

    # TODO: check that this fixes the problem
    if is_op(prev) and token_utils.is_comparison(bad.string + prev.string):
        cause = possible_cause.format(
            first=prev.string,
            second=bad.string,
            correct=bad.string + prev.string,
            wrong=prev.string + bad.string,
        )
        return {"cause": cause, "suggest": hint}
    elif is_op(next_) and token_utils.is_comparison(next_.string + bad.string):
        cause = possible_cause.format(
            first=bad.string,
            second=next_.string,
            correct=next_.string + bad.string,
            wrong=bad.string + next_.string,
        )
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def assign_instead_of_equal(statement):
    """Checks to see if an assignment sign, '=', has been used instead of
    an equal sign, '==', in an if, elif or while statement."""
    # TODO: generalize this for other situations by checking that the proposed
    # fix would work.
    _ = current_lang.translate

    if not statement.bad_token == "=":
        return {}

    if not statement.first_token.is_in(["if", "elif", "while"]):
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "==")
    if not fixers.check_statement(new_statement):
        # TODO: find a way to confirm that new error is later.
        debug_helper.log("Fix did not work in assign_instead_of_equal")
        additional_cause = _(
            "However, there might be some other errors in this statement.\n"
        )
    else:
        additional_cause = ""

    if sys.version_info < (3, 8):
        hint = _("Perhaps you needed `==` instead of `=`.\n")
        cause = _(
            "You used an assignment operator `=` instead of an equality operator `==`.\n"
        )
        return {"cause": cause + additional_cause, "suggest": hint}
    else:
        if statement.next_token == ":":
            hint = _("Perhaps you needed `:=` instead of `=:`.\n")
            cause = _(
                "You used an assignment operator `=` followed by `:`; perhaps you meant to use \n"
                "the walrus operator `:=`.\n"
            )
        else:
            hint = _("Perhaps you needed `==` or `:=` instead of `=`.\n")
            cause = _(
                "You used an assignment operator `=`; perhaps you meant to use \n"
                "an equality operator, `==`, or the walrus operator `:=`.\n"
            )
        return {"cause": cause + additional_cause, "suggest": hint}


@add_statement_analyzer
def print_as_statement(statement):
    _ = current_lang.translate

    if statement.prev_token == "print" and statement.bad_token != "(":
        cause = _(
            "In older version of Python, `print` was a keyword.\n"
            "Now, `print` is a function; you need to use parentheses to call it.\n"
        )
        return {"cause": cause}
    return {}


@add_statement_analyzer
def calling_pip(statement):
    _ = current_lang.translate
    if not statement.first_token.is_in(["pip", "python"]):
        return {}

    cause = _(
        "It looks as if you are attempting to use pip to install a module.\n"
        "`pip` is a command that needs to run in a terminal,\n"
        "not from a Python interpreter.\n"
    )

    for tok in statement.tokens:
        if tok == "pip":
            hint = _("Pip cannot be used in a Python interpreter.\n")
            return {"cause": cause, "suggest": hint}
    return {}


@add_statement_analyzer
def dot_followed_by_bracket(statement):
    _ = current_lang.translate

    if statement.bad_token.is_in("()[]{}") and statement.prev_token == ".":
        cause = _("You cannot have a dot `.` followed by `{bracket}`.\n").format(
            bracket=statement.bad_token
        )
    else:
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.prev_token, ",")
    if fixers.check_statement(new_statement):
        cause += _("Perhaps you need to replace the dot by a comma.\n")

    return {"cause": cause}


@add_statement_analyzer
def raise_single_exception(statement):
    _ = current_lang.translate
    if statement.first_token != "raise":
        return {}

    if statement.bad_token == "," and statement.prev_token.is_identifier():
        cause = _(
            "It looks like you are trying to raise an exception using Python 2 syntax.\n"
        )
        return {"cause": cause}
    return {}


@add_statement_analyzer
def invalid_double_star_operator(statement):
    _ = current_lang.translate

    if statement.bad_token == "**":
        cause = _(
            "The double star operator `**` is likely interpreted to mean that\n"
            "dict unpacking is to be used which does not make sense here.\n"
        )
        return {"cause": cause}

    return {}


@add_statement_analyzer
def missing_colon(statement):
    """look for missing colon at the end of statement"""
    _ = current_lang.translate

    if statement.last_token == ":" or statement.bad_token != statement.last_token:
        return {}

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
        return {}

    new_statement = fixers.modify_token(
        statement.tokens, statement.bad_token, append=":"
    )
    if not fixers.check_statement(new_statement):
        return {}

    name = statement.first_token

    hint = _("Did you forget a colon `:`?\n")

    if name.is_in(["for", "while"]):
        cause = _(
            "You wrote a `{for_while}` loop but\n"
            "forgot to add a colon `:` at the end\n"
            "\n"
        ).format(for_while=name)
        return {"cause": cause, "suggest": hint}
    elif name.is_in(["def", "elif", "else", "except", "finally", "if", "try", "with"]):
        cause = _(
            "You wrote a statement beginning with\n"
            "`{name}` but forgot to add a colon `:` at the end\n"
            "\n"
        ).format(name=name)
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def invalid_hexadecimal(statement):
    """Identifies problem caused by invalid character in an hexadecimal number."""
    _ = current_lang.translate

    prev = statement.prev_token
    wrong = statement.bad_token
    if not (prev.immediately_before(wrong) and prev.string.lower().startswith("0x")):
        return {}

    hint = _("Did you made a mistake in writing an hexadecimal integer?\n")
    cause = _(
        "It looks like you used an invalid character (`{character}`) in an hexadecimal number.\n\n"
        "Hexadecimal numbers are base 16 integers that use the symbols `0` to `9`\n"
        "to represent values 0 to 9, and the letters `a` to `f` (or `A` to `F`)\n"
        "to represent values 10 to 15.\n"
        "In Python, hexadecimal numbers start with either `0x` or `0X`,\n"
        "followed by the characters used to represent the value of that integer.\n"
    ).format(character=wrong.string[0])
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def invalid_octal(statement):
    """Identifies problem caused by invalid character in an octal number."""
    _ = current_lang.translate

    prev = statement.prev_token
    wrong = statement.bad_token
    if not (prev.immediately_before(wrong) and prev.string.lower().startswith("0o")):
        return {}

    hint = _("Did you made a mistake in writing an octal integer?\n")
    cause = _(
        "It looks like you used an invalid character (`{character}`) in an octal number.\n\n"
        "Octal numbers are base 8 integers that only use the symbols `0` to `7`\n"
        "to represent values.\n"
        "In Python, hexadecimal numbers start with either `0o` or `0O`,\n"
        "(the digit zero followed by the letter `o`)\n"
        "followed by the characters used to represent the value of that integer.\n"
    ).format(character=wrong.string[0])
    return {"cause": cause, "suggest": hint}


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
        return {"cause": cause, "suggest": hint}

    if first.is_complex():
        note = _("[Note: `{first}` is a complex number.]\n").format(first=first)
        second.string = first.string[-1] + second.string
        first.string = first.string[:-1]
    else:
        note = ""

    hint = _(
        "Perhaps you forgot a multiplication operator, `{first} * {second}`.\n"
    ).format(first=first, second=second)
    cause = cause

    return {"cause": cause + hint + "\n" + note, "suggest": hint}


@add_statement_analyzer
def debug_fstring(statement):
    """Detect debug feature of f-string introduced in Python 3.8"""
    _ = current_lang.translate
    if sys.version_info >= (3, 8) or not statement.fstring_error:
        return {}

    if statement.bad_token == "=" and statement.prev_token.is_identifier():
        if statement.next_token == ")":
            hint = _("Your Python version does not support this f-string feature.\n")
            cause = _(
                "You are likely using a 'debug' syntax of f-strings introduced\n"
                "in Python version 3.8. You are using version {version}.\n"
            ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")
            return {"cause": cause, "suggest": hint}
        else:
            cause = _(
                "You are likely trying to assign a value within an f-string.\n"
                "This is not allowed.\n"
            )
            return {"cause": cause}
    return {}


@add_statement_analyzer
def general_fstring_problem(statement=None):
    # General f-string problems are outside of our main priorities.
    _ = current_lang.translate
    if not statement.fstring_error:
        return {}

    cause = _(
        "The content of your f-string is invalid. Please consult the documentation:\n"
        "https://docs.python.org/3/reference/lexical_analysis.html#f-strings\n"
    )
    return {"cause": cause}


def def_correct_syntax():
    _ = current_lang.translate
    # fmt: off
    return _(
        "The correct syntax is:\n\n"
        "    def name ( ... ):"
    ) + "\n"
    # fmt: on


@add_statement_analyzer
def malformed_def_missing_parens(statement):
    # Something like
    # def test: ...
    _ = current_lang.translate

    if statement.first_token != "def":
        return {}

    if (
        statement.bad_token != ":"
        and statement.nb_tokens >= 3
        and statement.bad_token != statement.tokens[2]
    ):
        return {}

    new_statement = fixers.modify_token(
        statement.tokens, statement.bad_token, prepend="()"
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget parentheses?\n")
        cause = _(
            "Perhaps you forgot to include parentheses.\n"
            "You might have meant to write `{line}`\n"
        ).format(line=new_statement)
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def keyword_as_function_name(statement):
    # Something like
    # def pass() ...
    _ = current_lang.translate
    if (
        statement.first_token != "def"
        or not statement.bad_token.is_keyword()
        or not (statement.prev_token == statement.first_token)
    ):
        return {}

    hint = _("You cannot use a Python keyword as a function name.\n")
    cause = _(
        "You tried to use the Python keyword `{kwd}` as a function name.\n"
    ).format(kwd=statement.bad_token)

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if not fixers.check_statement(new_statement):
        cause += "\n" + _("There are more syntax errors later in your code.\n")

    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def other_invalid_function_names(statement):
    _ = current_lang.translate

    if (
        statement.first_token != "def"
        or statement.bad_token.is_identifier()
        or not (statement.prev_token == statement.first_token)
    ):
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if not fixers.check_statement(new_statement):
        return {}

    hint = _("You wrote an invalid function name.\n")
    cause = _(
        "The name of a function must be a valid Python identifier,\n"
        "that is a name that begins with a letter or an underscore character, `_`,\n"
        "and which contains only letters, digits or the underscore character.\n"
    )
    if statement.bad_token.is_string():
        cause += _("You attempted to use a string as a function name.\n")
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def function_definition_missing_name(statement):
    _ = current_lang.translate
    if not (
        statement.first_token == "def"
        and statement.bad_token == "("
        and statement.bad_token == statement.tokens[1]
    ):
        return {}

    cause = _("You forgot to name your function.\n") + def_correct_syntax()
    return {"cause": cause}


@add_statement_analyzer
def keyword_not_allowed_as_function_argument(statement):
    _ = current_lang.translate
    if not (
        statement.first_token == "def"
        and statement.bad_token.is_keyword()
        and statement.begin_brackets
    ):
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if not fixers.check_statement(new_statement):
        return {}

    cause = _(
        "I am guessing that you tried to use the Python keyword\n"
        "`{kwd}` as an argument in the definition of a function\n"
        "where an identifier (variable name) was expected.\n"
    ).format(kwd=statement.bad_token)

    return {"cause": cause}


@add_statement_analyzer
def malformed_def_begin_code_block(statement):
    # Thinking of def simply beginning a code block; something like
    # def : ...
    _ = current_lang.translate
    if statement.first_token != "def" or statement.bad_token != ":":
        return {}

    if not statement.prev_token == statement.first_token:
        return {}

    if statement.first_token.start_col == 0:
        cause = _(
            "You tried to define a function and did not use the correct syntax.\n"
        )
    else:
        cause = _(
            "You tried to define a function or method and did not use the correct syntax.\n"
        )
    cause += def_correct_syntax()

    return {"cause": cause}


@add_statement_analyzer
def malformed_class_begin_code_block(statement):
    # Thinking of class simply beginning a code block; something like
    # class : ...
    _ = current_lang.translate

    if statement.first_token != "class" or statement.bad_token != ":":
        return {}

    if not statement.prev_token == statement.first_token:
        return {}

    cause = _("You tried to define a class and did not use the correct syntax.\n")
    return {"cause": cause}


@add_statement_analyzer
def assign_to_a_keyword(statement):
    """Checks to see if line is of the form 'keyword = ...'"""
    _ = current_lang.translate
    possible_cause = _(
        "You were trying to assign a value to the Python keyword `{keyword}`.\n"
        "This is not allowed.\n"
        "\n"
    )
    if statement.bad_token == "=" and statement.prev_token.is_keyword():
        cause = possible_cause.format(keyword=statement.prev_token)
    elif statement.bad_token.is_keyword() and statement.next_token == "=":
        cause = possible_cause.format(keyword=statement.bad_token)
    else:
        return {}
    return {"cause": cause}


@add_statement_analyzer
def missing_comma_before_string_in_dict(statement):
    """Special case where keys and values in a dict are strings which are
    not separated by commas."""
    _ = current_lang.translate
    cause = hint = None

    # This is a bit of an usual case as the error occurred due to a forgotten comma
    # two tokens before the token flagged by Python.
    if not (
        statement.begin_brackets
        and statement.begin_brackets[-1] == "{"
        and statement.bad_token == ":"
        and statement.prev_token.is_string()
        and statement.tokens[statement.bad_token_index - 1].is_string()
    ):
        return cause, hint

    new_statement = fixers.modify_token(
        statement.tokens, statement.prev_token, prepend=","
    )
    if fixers.check_statement(new_statement):
        cause = _(
            "I am guessing that you forgot a comma between two strings\n"
            "when defining a dict.\n\n"
        ).format(kwd=statement.bad_token)
        new_statement = fixers.modify_token(
            statement.tokens, statement.prev_token, prepend=" «,» "
        )
        cause += "```\n" + new_statement + "\n```"
        hint = _("Did you forget a comma?\n")

    return cause, hint


def _perhaps_misspelled_keyword(tokens, wrong):
    kwlist = list(keyword.kwlist)
    # Make sure we try possible typos first
    similar = utils.get_similar_words(wrong.string, kwlist)

    # The 'except' and 'with' keywords can apparently appear in similar situations
    # as 'for', 'if', etc., without raising any SyntaxErrors.
    # Furthermore, while it might be syntactically correct to have something like
    # else: statement_on_one_Line
    # it should be avoided as it could lead to incorrect suggestions.
    # Also, since 'if' can be used wherever 'elif' is acceptable, we exclude elif
    excluded = [
        word
        for word in ["except", "with", "else", "finally", "try", "elif"]
        if word not in similar
    ]

    # 'not' can be used in many places, most of which would likely not make sense
    # as additional suggestions
    kwlist.remove("not")
    words = [word for word in kwlist if word not in similar]
    similar.extend(words)
    results = []
    for word in similar:
        new_statement = fixers.replace_token(tokens, wrong, word)
        if fixers.check_statement(new_statement):
            results.append((word, new_statement))

    if len(results) > 1:
        results = [(word, line) for word, line in results if word not in excluded]
    return results


def _add_comma_or_operator(tokens, tok, comma_first=True):
    if comma_first:
        operators = ",", " +", " -", " *", " in"
    else:
        operators = " +", " -", " *", ",", " in"
    results = []
    for operator in operators:
        if operator == " in" and results:
            break
        new_statement = fixers.modify_token(tokens, tok, append=operator)
        if fixers.check_statement(new_statement):
            if operator == "," and results:  # So that it prints correctly
                operator = '","'
            results.append((operator.strip(), new_statement))
    return results


def _comma_first_cause(bracket):
    _ = current_lang.translate
    if bracket == "(":
        return _(
            "It is possible that you "
            "forgot a comma between items in a tuple, \n"
            "or between function arguments, \n"
            "before the position indicated by --> and ^.\n"
        )
    elif bracket == "[":
        return _(
            "It is possible that you "
            "forgot a comma between items in a list\n"
            "before the position indicated by --> and ^.\n"
        )
    else:
        return _(
            "It is possible that you "
            "forgot a comma between items in a set or dict\n"
            "before the position indicated by --> and ^.\n"
        )


@add_statement_analyzer
def missing_comma_or_operator(statement):
    """Check to see if a comma or other operator
    is possibly missing between identifiers, or numbers, or both.
    """
    # TODO: refactor this
    _ = current_lang.translate
    cause = hint = None

    bad_token = statement.bad_token
    if not (
        bad_token.is_identifier() or bad_token.is_number() or bad_token.is_string()
    ):
        return cause, hint

    prev_token = statement.prev_token
    if not (
        prev_token.is_identifier() or prev_token.is_number() or prev_token.is_string()
    ):
        return cause, hint

    possible_cause = _(
        "Python indicates that the error is caused by "
        "`{second}` written immediately after `{first}`.\n"
    ).format(first=prev_token, second=bad_token)

    if statement.begin_brackets:
        # likely inside a list, tuple, function def, dict, ...
        # in which case the most likely cause is a missing comma
        comma_first = True
        bracket = statement.begin_brackets[-1]
        comma_first_cause = _comma_first_cause(bracket)
    else:
        comma_first = False
        comma_first_cause = ""

    results = _add_comma_or_operator(
        statement.tokens, prev_token, comma_first=comma_first
    )

    if results:
        if (
            len(results) == 1
            or statement.first_token == "def"
            or statement.first_token == "class"
        ):
            operator, line = results[0]
            if "," in operator:
                hint = _("Did you forget a comma?\n")
                cause = possible_cause + comma_first_cause
                cause += _("Perhaps you meant\n\n    {line}\n").format(line=line)
            else:
                hint = _("Did you mean `{line}`?\n").format(line=line)
                cause = possible_cause
        else:
            operators = [operator for operator, line in results]
            lines = [line for operator, line in results]
            hint = _(
                "Did you forget something between `{first}` and `{second}`?\n"
            ).format(first=prev_token, second=bad_token)

            # The list of operators might include a comma; it is better to separate
            # items by semi-colons
            if comma_first:
                operators = operators[1:]
                operators = utils.list_to_string(operators)
            else:
                operators = utils.list_to_string(operators, sep="; ")

            cause = (
                possible_cause
                + comma_first_cause
                + _(
                    "Perhaps you meant to insert an operator like `{operators}`\n"
                    "between `{first}` and `{second}`.\n"
                    "The following lines of code would not cause any `SyntaxError`:\n\n"
                ).format(first=prev_token, second=bad_token, operators=operators)
            )
            for line in lines:
                cause += f"    {line}\n"

            cause += _(
                "Note: these are just some of the possible choices and that\n"
                "some of them might raise other types of exceptions.\n"
            )

    # special case; something like
    # my name = "André"
    # instead of  my_name = ...
    # See more general handling in space_in_identifiers() below
    if cause and prev_token is statement.first_token:
        first_tokens = []
        line = None
        for tok in statement.tokens:
            if tok == "=":
                line = token_utils.untokenize(statement.tokens)
                begin, end = line.split("=", 1)
                line = "_".join(first_tokens) + " =" + end
                cause += (
                    "\n"
                    + _(
                        "Or perhaps you forgot that you cannot have spaces\n"
                        "in variable names.\n"
                    )
                    + f"\n\n    {line}\n"
                )
                break
            elif not tok.is_identifier():
                break
            else:
                first_tokens.append(tok.string)
        if line:
            hint = _("Did you mean `{line}`?\n").format(line=line)
    elif prev_token.is_identifier():
        new_statement = fixers.replace_two_tokens(
            statement.tokens,
            prev_token,
            prev_token.string + "_" + bad_token.string,
            bad_token,
            "",
        )
        if fixers.check_statement(new_statement):
            if cause is None:
                cause = ""
            cause += _(
                "Perhaps you forgot that you cannot have spaces\n"
                "in variable names and wrote `'{first} {second}'`\n"
                "instead of `'{first}_{second}'`.\n"
            ).format(first=prev_token, second=bad_token)
        if hint is None:
            hint = _("Did you mean `'{first}_{second}'`?\n").format(
                first=prev_token, second=bad_token
            )
        elif statement.first_token != "def" and statement.first_token != "class":
            hint = _("Did you mean `'{first}_{second}'`?\n").format(
                first=prev_token, second=bad_token
            )

    return cause, hint


def misspelled_python_keyword(tokens, bad_token):
    _ = current_lang.translate
    cause = hint = None

    results = _perhaps_misspelled_keyword(tokens, bad_token)
    if results:
        if len(results) == 1:
            word, line = results[0]
            hint = _("Did you mean `{line}`?\n").format(line=line)

            cause = _(
                "Perhaps you meant to write `{keyword}` and made a typo.\n"
                "The correct line would then be `{line}`\n"
            ).format(keyword=word, line=line)
        else:
            lines = [line for _word, line in results]
            hint = _("Did you mean `{line}`?\n").format(line=lines[0])

            cause = _(
                "Perhaps you wrote another word instead of a Python keyword.\n"
                "If that is the case, perhaps you meant to write one of\n"
                "the following lines of code which might not raise a `SyntaxError`:\n\n"
            )
            for line in lines:
                cause += f"    {line}\n"

    return cause, hint


@add_statement_analyzer
def current_is_misspelled_python_keyword(statement):
    _ = current_lang.translate
    cause = hint = None

    if not statement.bad_token.is_identifier():
        return cause, hint
    return misspelled_python_keyword(statement.tokens, statement.bad_token)


@add_statement_analyzer
def previous_is_misspelled_python_keyword(statement):
    _ = current_lang.translate
    cause = hint = None

    if not statement.prev_token.is_identifier():
        return cause, hint
    return misspelled_python_keyword(statement.tokens, statement.prev_token)


@add_statement_analyzer
def equal_instead_of_colon_in_dict(statement):
    _ = current_lang.translate
    cause = hint = None

    if not (statement.begin_brackets and statement.bad_token == "="):
        return cause, hint

    if statement.begin_brackets[-1] == "{":
        cause = _(
            "It is possible that "
            "you used an equal sign `=` instead of a colon `:`\n"
            "to assign values to keys in a dict\n"
            "before or at the position indicated by --> and ^.\n"
        )

    return cause, hint


@add_statement_analyzer
def consecutive_operators(statement):
    _ = current_lang.translate
    cause = hint = None
    is_op = token_utils.is_operator

    if not (is_op(statement.bad_token) and is_op(statement.prev_token)):
        return cause, hint

    if statement.bad_token == "=" and statement.prev_token == "==":
        cause = _(
            "You wrote three equal signs in a row which is allowed in some\n"
            "programming languages, but not in Python. To check if two objects\n"
            "are equal, use two equal signs, `==`; to see if two names represent\n"
            "the exact same object, use the operator `is`.\n"
        )
        hint = _("Did you mean to use `is` instead of `===`?\n")
    elif statement.bad_token == statement.prev_token:
        cause = _(
            "You cannot have write the same operator, `{op}`, twice in a row.\n"
            "Perhaps you wrote one of them by mistake\n"
            "or forgot to write something between them.\n"
        ).format(op=statement.prev_token)
    else:
        cause = _(
            "You cannot have these two operators, `{first}` and `{second}`,\n"
            "following each other. Perhaps you wrote one of them by mistake\n"
            "or forgot to write something between them.\n"
        ).format(first=statement.prev_token, second=statement.bad_token)

    return cause, hint


@add_statement_analyzer
def dotted_name_in_def(statement):
    _ = current_lang.translate
    cause = hint = None

    if not (statement.bad_token == "." and statement.first_token == "def"):
        return cause, hint

    cause = _("You cannot use dotted names as function arguments.\n")

    return cause, hint


@add_statement_analyzer
def positional_arguments_in_def(statement):
    _ = current_lang.translate
    cause = hint = None

    if not (statement.bad_token == "/" and statement.first_token == "def"):
        return cause, hint

    prev_tok = ""
    for tok in statement.tokens:
        if tok == "*":
            cause = _(
                "`/` indicates that the previous arguments in a function definition\n"
                "are positional arguments. However, `*` indicates that the arguments\n"
                "that follow must be keyword arguments.\n"
                "When they are used together, `/` must appear before `*`.\n"
            )
            hint = _("`*` must appear after `/` in a function definition.\n")
            return cause, hint
        elif tok is statement.bad_token:
            break
        elif tok == "/" and prev_tok == ",":
            cause = _("You can only use `/` once in a function definition.\n")
            return cause, hint
        prev_tok = tok
    return cause, hint


@add_statement_analyzer
def keyword_arguments_in_def(statement):
    _ = current_lang.translate
    cause = hint = None

    if not (statement.bad_token == "*" and statement.first_token == "def"):
        return cause, hint

    prev_tok = ""
    for tok in statement.tokens:
        if tok is statement.bad_token:
            break
        elif tok == "*" and prev_tok == ",":
            cause = _("You can only use `*` once in a function definition.\n")
            return cause, hint
        prev_tok = tok
    return cause, hint


@add_statement_analyzer
def and_instead_of_comma(statement):
    # Example: from math import sin and cos
    _ = current_lang.translate
    cause = hint = None

    if not statement.bad_token == "and":
        return cause, hint

    possible_cause = _(
        "The Python keyword `and` can only be used for boolean expressions.\n"
        "Perhaps you meant to write\n\n"
        "`{new_statement}`\n"
    )

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, ",")
    if fixers.check_statement(new_statement):
        cause = possible_cause.format(new_statement=new_statement)
    else:  # 'and' following a comma
        new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "")
        if fixers.check_statement(new_statement):
            cause = possible_cause.format(new_statement=new_statement)

    return cause, hint


@add_statement_analyzer
def from_import_as(statement):
    """from module import ... as ..., with 'as' flagged as the bad token"""
    _ = current_lang.translate
    cause = hint = None
    if not (
        statement.bad_token == "as"
        and statement.first_token == "from"
        and statement.tokens[2] == "import"
    ):
        return cause, hint

    cause = _(
        "I am guessing that you are trying to import at least one object\n"
        "from module `{module}` and rename it using the Python keyword `as`;\n"
        "this keyword can only be used to rename one object at a time\n"
        "using a well defined syntax.\n"
        "I suggest that you split up any such import statement with each object\n"
        "renamed on a separate line as follows:\n\n"
        "    from {module} import object_1 as name_1\n"
        "    from {module} import object_2 as name_2  # if needed\n"
    ).format(module=statement.tokens[1])
    return cause, hint


# Keep last
@add_statement_analyzer
def unclosed_bracket(statement):
    _ = current_lang.translate
    cause = hint = None

    if not statement.statement_brackets:
        return cause, hint

    bracket = statement.begin_brackets[0]
    linenumber = bracket.start_row
    start_col = bracket.start_col

    bracket_name = syntax_utils.name_bracket(bracket)
    source = f"\n    {linenumber}: {statement.source_lines[linenumber - 1]}"
    shift = len(str(linenumber)) + start_col + 6
    source += " " * shift + "|\n"

    cause = (
        _("The opening {bracket} on line {linenumber} is not closed.\n").format(
            bracket=bracket_name, linenumber=linenumber
        )
        + source
    )
    return cause, hint
