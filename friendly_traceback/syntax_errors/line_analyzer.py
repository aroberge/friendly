"""This module contains functions that are used to
   analyze a single line of code which has been identified
   as containing a syntax error with the message "invalid syntax".
"""
import sys

from .. import debug_helper
from .. import utils
from ..my_gettext import current_lang


def count_char(tokens, char):
    """Counts how many times a given character appears in a list of tokens"""
    return sum(1 for token in tokens if token == char)


def find_offending_token(tokens, offset):
    """Based on the offset provided by Python in the traceback, we find
    the token that was flagged as being in error.
    """
    # Note that the offset provided by Python starts at 1 instead of 0
    offset -= 1  # shift for proper comparison
    for index, tok in enumerate(tokens):
        if tok.start_col == offset:
            return tok, index
    return None, None


def is_potential_statement(tokens):
    """This helper function tests the list of tokens
       (usually corresponding to a single line of code)
       and returns True if the corresponding line of code could possibly be a
       complete Python statement as described below.

       A complete Python statement would have brackets,
       including (), [], and {}, matched in pairs,
       and would not end with the continuation character \\
    """
    line = tokens[0].line

    # All tokens passed should come from the same line of code
    if tokens[-1].line != line:
        debug_helper.log("In line_analyzer.is_potential_statement()")
        debug_helper.log("Not all tokens came from the same line.")
        return False

    if line.endswith("\\"):
        return False

    return (
        (count_char(tokens, "(") == count_char(tokens, ")"))
        and (count_char(tokens, "[") == count_char(tokens, "]"))
        and (count_char(tokens, "{") == count_char(tokens, "}"))
    )


LINE_ANALYZERS = []


def add_line_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single line of code."""
    LINE_ANALYZERS.append(func)

    def wrapper(tokens, offset=None):
        return func(tokens, offset=offset)

    return wrapper


# ========================================================
# Main calling function
# ========================================================


def analyze_last_line(line, offset=None):
    """Analyzes the last line of code as identified by Python as that
    on which the error occurred."""
    tokens = utils.tokenize_source(line)  # tokens do not include spaces nor comments

    if not tokens:
        return None, None

    for analyzer in LINE_ANALYZERS:
        cause, hint = analyzer(tokens, offset=offset)
        if cause:
            return cause, hint
    return None, None


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order can yield incorrect results
# ==================


@add_line_analyzer
def copy_pasted_code(tokens, **kwargs):
    """Detecting code that starts with a Python prompt"""
    _ = current_lang.translate
    cause = hint = None
    if len(tokens) < 2:
        return cause, hint
    if tokens[0] == ">>" and tokens[1] == ">":
        cause = _(
            "It looks like you copy-pasted code from an interactive interpreter.\n"
            "The Python prompt, `>>>`, should not be included in your code.\n"
        )
        hint = _("Did you use copy-paste?\n")
    return cause, hint


@add_line_analyzer
def detect_walrus(tokens, offset=None):
    """Detecting if code uses named assignment operator := with an
    older version of Python.
    """
    _ = current_lang.translate
    cause = hint = None
    if sys.version_info >= (3, 8):
        return cause, hint

    bad_token, index = find_offending_token(tokens, offset)
    if bad_token is None or bad_token != ":":
        return cause, hint

    try:
        next_token = tokens[index + 1]
    except IndexError:
        return cause, hint

    if next_token != "=":
        return cause, hint

    hint = _("Your Python version might be too old.\n")
    cause = _(
        "You appear to be using the operator `:=`, sometimes called\n"
        "the walrus operator. This operator requires the use of\n"
        "Python 3.8 or newer. You are using version {version}.\n"
    ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")
    return cause, hint


@add_line_analyzer
def debug_f_string(tokens, offset=None):
    """detect debug feature of f-string introduced in Python 3.8"""
    _ = current_lang.translate
    cause = hint = None
    if sys.version_info >= (3, 8):
        return cause, hint
    if len(tokens) != 4:
        return cause, hint

    if (
        tokens[0] == "("
        and tokens[1].is_identifier()
        and tokens[2] == "="
        and tokens[3] == ")"
    ):
        cause = _(
            "You are likely using a syntax of f-strings introduced\n"
            "in Python version 3.8. You are using version {version}.\n"
        ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")
    return cause, hint


@add_line_analyzer
def detect_backquote(tokens, offset=None):
    """Detecting if the error is due to using `x` which was allowed
    in Python 2.
    """
    _ = current_lang.translate
    cause = hint = None
    bad_token, ignore = find_offending_token(tokens, offset)
    if bad_token is None:
        return cause, hint
    # the token that gets flagged as problematic is the one after ""
    if bad_token == "`":
        hint = _("You should not use the backquote character.\n")
        cause = _(
            "You are using the backquote character.\n"
            "Either you meant to write a single quote, ', "
            "or copied Python 2 code;\n"
            "in this latter case, use the function `repr(x)`."
        )
    return cause, hint


@add_line_analyzer
def assign_to_a_keyword(tokens, **kwargs):
    """Checks to see if line is of the form 'keyword = ...'"""
    _ = current_lang.translate
    cause = hint = None
    if len(tokens) < 2 or (not tokens[0].is_keyword()) or tokens[1] != "=":
        return cause, hint

    cause = _(
        "You were trying to assign a value to the Python keyword `{keyword}`.\n"
        "This is not allowed.\n"
        "\n"
    ).format(keyword=tokens[0])
    return cause, hint


@add_line_analyzer
def confused_elif(tokens, **kwargs):
    _ = current_lang.translate
    cause = hint = None
    name = None
    if tokens[0] == "elseif":
        name = "elseif"
    elif tokens[0] == "else" and len(tokens) > 1 and tokens[1] == "if":
        name = "else if"
    if name:
        hint = _("Perhaps you meant to write `elif`.\n")
        cause = _(
            "You likely meant to use Python's `elif` keyword\n"
            "but wrote `{name}` instead\n"
            "\n"
        ).format(name=name)
    return cause, hint


@add_line_analyzer
def import_from(tokens, **kwargs):
    _ = current_lang.translate
    cause = hint = None
    if len(tokens) < 4:
        return cause, hint
    if tokens[0] != "import":
        return cause, hint
    if tokens[2] == "from":
        function = tokens[1]
        module = tokens[3]
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


@add_line_analyzer
def keyword_as_attribute(tokens, **kwargs):
    """Will identify something like  obj.True ..."""
    _ = current_lang.translate
    cause = hint = None
    prev_word = None
    for word in tokens:
        if prev_word == ".":
            if word.is_keyword():
                cause = _(
                    "You cannot use the Python keyword `{word}` as an attribute.\n\n"
                ).format(word=word)
                break
            elif word == "__debug__":
                cause = _(
                    "You cannot use the constant `__debug__` as an attribute.\n\n"
                )
                break
        else:
            prev_word = word
    return cause, hint


@add_line_analyzer
def misplaced_quote(tokens, **kwargs):
    """This looks for a misplaced quote, something like
       info = 'don't' ...

    The clue we are looking for is a STRING token ('don')
    followed by a NAME token (t).
    """
    _ = current_lang.translate
    cause = hint = None
    if len(tokens) < 2:
        return cause, hint
    prev = tokens[0]
    for token in tokens:
        if prev.is_string() and token.is_name():
            hint = _("Perhaps you misplaced a quote.\n")
            cause = _(
                "There appears to be a Python identifier (variable name)\n"
                "immediately following a string.\n"
                "I suspect that you were trying to use a quote inside a string\n"
                "that was enclosed in quotes of the same kind.\n"
            )
            break
        prev = token
    return cause, hint


@add_line_analyzer
def assign_instead_of_equal(tokens, offset=None):
    """Checks to see if an assignment sign, '=', has been used instead of
    an equal sign, '==', in an if or elif statement."""
    _ = current_lang.translate
    cause = hint = None
    if not tokens[0].is_in(["if", "elif", "while"]):
        return cause, hint

    bad_token, ignore = find_offending_token(tokens, offset)
    equal = _("Perhaps you needed `==` instead of `=`.\n")
    equal_or_walrus = _("Perhaps you needed `==` or `:=` instead of `=`.\n")
    if bad_token == "=":
        statement = tokens[0]
        if statement.is_in(["if", "elif"]):
            cause = _(
                "You used an assignment operator `=` instead of an equality operator `==` \n"
                "with an `{if_elif}` statement.\n"
            ).format(if_elif=statement)
            hint = equal
        elif sys.version_info < (3, 8):
            cause = _(
                "You used an assignment operator `=` instead of an equality operator `==` \n"
                "with a `{while_}` statement.\n"
            ).format(while_=statement)
            hint = equal
        else:
            cause = _(
                "You used an assignment operator `=`; perhaps you meant to use \n"
                "an equality operator, `==`, or the walrus operator `:=`.\n"
            )
            hint = equal_or_walrus
    return cause, hint


@add_line_analyzer
def missing_colon(tokens, **kwargs):
    """look for missing colon at the end of statement"""
    _ = current_lang.translate
    cause = hint = None

    if tokens[-1] == ":":
        return cause, hint

    if not is_potential_statement(tokens):
        return cause, hint

    name = tokens[0]

    forgot_a_colon = _("Perhaps you forgot a colon `:`.\n")

    if name == "class":
        name = _("a class")
        cause = _(
            "You wanted to define `{class_}`\n"
            "but forgot to add a colon `:` at the end\n"
            "\n"
        ).format(class_=name)
        hint = forgot_a_colon
    elif name.is_in(["for", "while"]):
        cause = _(
            "You wrote a `{for_while}` loop but\n"
            "forgot to add a colon `:` at the end\n"
            "\n"
        ).format(for_while=name)
        hint = forgot_a_colon
    elif name.is_in(["def", "elif", "else", "except", "finally", "if", "try"]):
        cause = _(
            "You wrote a statement beginning with\n"
            "`{name}` but forgot to add a colon `:` at the end\n"
            "\n"
        ).format(name=name)
        hint = forgot_a_colon

    return cause, hint


@add_line_analyzer
def malformed_def(tokens, **kwargs):
    """Looks for problems with defining a function, assuming that
    the information passed looks like a complete statement"""
    _ = current_lang.translate
    cause = hint = None
    if tokens[0] != "def":
        return cause, hint

    if not is_potential_statement(tokens):
        return cause, hint

    if len(tokens) >= 3 and tokens[1].is_identifier() and tokens[2] == ":":
        hint = _("Perhaps you forgot parentheses.\n")
    # need at least five tokens: def name ( ) :
    if (
        len(tokens) < 5
        or not tokens[1].is_name()
        or tokens[2] != "("
        or tokens[-2] != ")"
        or tokens[-1] != ":"
    ):
        name = _("a function or method")
        cause = _(
            "You tried to define {class_or_function} "
            "and did not use the correct syntax.\n"
            "The correct syntax is:\n\n"
            "    def name ( optional_arguments ):"
            "\n"
        ).format(class_or_function=name)
        return cause, hint

    fn_name = tokens[1]
    if fn_name.is_keyword():
        cause = _(
            "You tried to use the Python keyword `{kwd}` as a function name.\n"
        ).format(kwd=fn_name)
        return cause, hint

    # Lets look at the possibility that a keyword might have been used
    # as an argument or keyword argument. The following test is admiteddly
    # crude and imperfect, but it is the last one we do.

    prev_token_str = None
    parens = 0
    brackets = 0
    curly = 0
    for index, tok in enumerate(tokens):
        # Note, we know that a SyntaxError: invalid syntax occurred.
        # So, while some cases of the following might be ok, we assume here that
        # they might have caused the error. They might include things like:
        # def test(None ...)  or
        # def test(*None ...) or
        # def test(**None ...) or
        # def test(a, None ...)
        #       but not
        # def test(a=None ...) nor
        # def test(a=(None,...)) nor
        # def test(a = [1, None])
        if tok == "(":
            parens += 1
        elif tok == ")":
            parens -= 1
        elif tok == "[":
            brackets += 1
        elif tok == "]":
            brackets -= 1
        elif tok == "{":
            curly += 1
        elif tok == "}":
            curly -= 1

        elif tok.is_keyword() and (
            (prev_token_str == "(" and index == 3)  # first argument
            or (
                parens % 2 == 1
                and brackets % 2 == 0
                and curly % 2 == 0
                and prev_token_str in [",", "*", "**"]
            )
        ):
            return (
                _(
                    "I am guessing that you tried to use the Python keyword\n"
                    "`{kwd}` as an argument in the definition of a function.\n"
                ).format(kwd=tok),
                None,
            )
            # break
        prev_token_str = tok
    return cause, hint


@add_line_analyzer
def print_as_statement(tokens, **kwargs):
    _ = current_lang.translate
    cause = hint = None
    if tokens[0] != "print":
        return cause, hint

    # TODO: add hint
    if len(tokens) == 1 or tokens[1] != "(":
        cause = _(
            "In older version of Python, `print` was a keyword.\n"
            "Now, `print` is a function; you need to use parentheses to call it.\n"
        )
    return cause, hint


@add_line_analyzer
def calling_pip(tokens, **kwargs):
    _ = current_lang.translate
    cause = hint = None
    if not tokens[0].is_in(["pip", "python"]):
        return cause, hint

    use_pip = _(
        "It looks as if you are attempting to use pip to install a module.\n"
        "`pip` is a command that needs to run in a terminal,\n"
        "not from a Python interpreter.\n"
    )

    for tok in tokens:
        if tok == "pip":
            hint = _("Pip cannot be used in a Python interpreter.\n")
            return use_pip, hint
    return cause, hint


@add_line_analyzer
def dot_followed_by_bracket(tokens, offset=None):
    _ = current_lang.translate
    cause = hint = None
    bad_token, index = find_offending_token(tokens, offset)
    if bad_token is None or index == 0:
        return cause, hint
    prev_token = tokens[index - 1]
    if bad_token.is_in(["(", ")", "[", "]", "{", "}"]) and prev_token == ".":
        cause = _("You cannot have a dot `.` followed by `{bracket}`.\n").format(
            bracket=bad_token
        )
    return cause, hint


@add_line_analyzer
def raise_single_exception(tokens, offset=None):
    _ = current_lang.translate
    cause = hint = None
    if tokens[0] != "raise":
        return cause, hint
    bad_token, ignore = find_offending_token(tokens, offset)
    if bad_token is None:
        return cause, hint
    if bad_token == ",":
        cause = _(
            "It looks like you are trying to raise an exception using Python 2 syntax.\n"
        )
    return cause, hint


@add_line_analyzer
def invalid_name(tokens, offset=None):
    """Identifies invalid identifiers when a name begins with a number"""
    _ = current_lang.translate
    cause = hint = None

    if len(tokens) < 2:
        return cause, hint

    note = None
    for first, second in zip(tokens, tokens[1:]):
        if first.is_number() and second.is_identifier() and first.end == second.start:
            cause = _("Valid names cannot begin with a number.\n")
            if first.is_complex():
                note = _("[Note: `{first}` is a complex number.]\n").format(first=first)
                second.string = first.string[-1] + second.string
                first.string = first.string[:-1]
            if second == "i" and first != tokens[0]:
                hint = _("Did you mean `{number}j`?\n").format(number=first)
                cause += _(
                    "Perhaps you thought that `i` could be used to represent\n"
                    "the square root of -1. In Python, `j` (or `1j`) is used for this\n"
                    "and perhaps you meant to write `{number}j`.\n"
                ).format(number=first)
                return cause, hint
            break

    # Try to distinguish between  "2x = ... and y = ... 2x ..."
    if cause:
        tokens.append(";")
        for first, second, third in zip(tokens, tokens[1:], tokens[2:]):
            if (
                first.is_number()
                and second.is_identifier()
                and first.end == second.start
            ):
                if third != "=":
                    hint = _(
                        "Perhaps you forgot a multiplication operator,"
                        " `{first} * {second}`.\n"
                    ).format(first=first, second=second)
                    cause = cause + hint
                else:
                    hint = cause
                break
    if note is not None:
        cause += "\n" + note
    return cause, hint


@add_line_analyzer
def missing_comma_or_operator(tokens, offset=None):
    """Check to see if a comma or other operator
    is possibly missing between identifiers, or numbers, or both.
    """
    _ = current_lang.translate
    cause = hint = None

    if len(tokens) < 2:
        return cause, hint

    for first, second in zip(tokens, tokens[1:]):
        if (
            first.is_number()
            and not first.is_complex()  # should not be needed as the preceding
            # function should have caught this.
            and second == "i"
            and first.end == second.start
        ):
            hint = _("Did you mean `{number}j`?\n").format(number=first)
            cause = (
                "Perhaps you thought that `i` could be used to represent\n"
                "the square root of -1.\n"
                "In Python, `j` immediately following a number is used for this.\n"
                "Perhaps you meant to write `{number}j`.\n"
            ).format(number=first)
            return cause, hint
        if (
            (first.is_number() or first.is_identifier() or first.is_string())
            and (second.is_number() or second.is_identifier() or second.is_string())
            and second.start_col <= offset <= second.end_col
        ):

            hint = _(
                "Did you forget something between `{first}` and `{second}`?\n"
            ).format(first=first, second=second)

            cause = _(
                "Python indicates that the error is caused by "
                "`{second}` written just after `{first}`.\n"
                "Perhaps you forgot a comma or an operator, like `+`, `*`, `in`, etc., "
                "between `{first}` and `{second}`.\n"
            ).format(first=first, second=second)

            # User might want to define "my name = 'Python'"
            if first == tokens[0]:
                for tok in tokens:
                    if tok == "=":
                        cause += _(
                            "Or perhaps you forgot that you cannot have spaces\n"
                            "in variable names.\n"
                        )
                        break
                    elif not tok.is_identifier():
                        break
            return cause, hint
    return cause, hint


@add_line_analyzer
def invalid_double_star_operator(tokens, offset=None):
    _ = current_lang.translate
    cause = hint = None

    possible_cause = _(
        "The double star operator `**` is likely interpreted to mean that\n"
        "dict unpacking is to be used which does not make sense here.\n"
    )

    if tokens[0] == "**":
        return possible_cause, hint

    if sys.version_info < (3, 8):  # not getting the right info from fstrings
        for prev_token, token in zip(tokens, tokens[1:]):
            if prev_token == "(" and token == "**":
                return possible_cause, hint

    bad_token, index = find_offending_token(tokens, offset)
    if bad_token == "**":
        return possible_cause, hint

    return cause, hint
