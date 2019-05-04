"""analyze_syntax.py

Attempts to find the most likely cause of a SyntaxError.
"""

import keyword
import tokenize

from .my_gettext import current_lang
from .utils import collect_tokens

possible_causes = []


def add_cause(func):
    """A simple decorator that adds a given cause to the list
       of probable causes."""
    possible_causes.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


def find_likely_cause(source, linenumber, message, offset):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """

    offending_line = source[linenumber - 1]
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides.
    if message == "can't assign to literal":
        return assign_to_literal(message, line)

    # If not, we guess based on the content of the last line of code
    # Note: we will need to do more than this to catch other types
    # of errors, such as mismatched brackets, etc.
    return analyze_last_line(line)


def assign_to_literal(message, line):
    variable = line.split("=")[0].strip()
    return message + " %s" % variable


def analyze_last_line(line):
    """Analyzes the last line of code as identified by Python as that
       on which the error occurred."""
    tokens = collect_tokens(line)

    if not tokens:
        return "No cause found"

    for possible in possible_causes:
        cause = possible(tokens)
        if cause:
            return cause
    return "No cause found"


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order can yield incorrect results
# ==================


@add_cause
def assign_to_a_keyword(tokens):
    """Checks to see if it is of the formm

       keyword = ...
    """
    if len(tokens) < 2:
        return False
    if tokens[0].string not in keyword.kwlist:
        return False

    if tokens[1].string == "=":
        return "Assigning to Python keyword"
    return False


@add_cause
def confused_elif(tokens):
    if tokens[0].string == "elseif":
        return "elif not elseif"

    if tokens[0].string == "else" and len(tokens) > 1 and tokens[1].string == "if":
        return "elif not else if"
    return False


@add_cause
def import_from(tokens):
    """Looks for
            import X from Y
       instead of
            from Y import X
    """
    if len(tokens) < 4:
        return
    first = tokens[0].string
    if first != "import":
        return
    third = tokens[2].string
    if third == "from":
        return "import X from Y"
    return False


@add_cause
def missing_colon(tokens):
    # needs unit tests:
    if len(tokens) < 2:
        return False

    name = tokens[0].string
    if name in [
        "class",
        "def",
        "elif",
        "else",
        "except",
        "finally",
        "if",
        "for",
        "while",
        "try",
    ]:
        last = tokens[-1]
        if last.string != ":":
            return "%s missing colon" % name
    return False


@add_cause
def malformed_def(tokens):
    # need at least five tokens: def name ( ) :
    if tokens[0].string != "def":
        return False

    if (
        len(tokens) < 5
        or tokens[1].type != tokenize.NAME
        or tokens[2].string != "("
        or tokens[-2].string != ")"
        or tokens[-1].string != ":"
    ):
        return "malformed def"

    return False


# ======================
# Proper text conversion
# ======================


def expand_cause(cause):
    """Returns a written explanation given an abbreviated form"""
    _ = current_lang.lang

    if cause == "Assigning to Python keyword":
        return _(
            "    My best guess: you were trying\n"
            "    to assign a value to a Python keyword.\n"
            "    This is not allowed.\n"
            "\n"
        )

    if cause == "import X from Y":
        return _(
            "    My best guess: you wrote something like\n"
            "        import X from Y\n"
            "    instead of\n"
            "        from Y import X\n"
            "\n"
        )

    if cause.startswith("elif not"):
        cause = cause.replace("elif not ", "")
        return _(
            "    My best guess: you meant to use Python's 'elif' keyword\n"
            "    but wrote '{name}' instead\n"
            "\n"
        ).format(name=cause)

    if cause.endswith("missing colon"):
        name = cause.split(" ")[0]
        if name == "class":
            name = _("a class")
            return _(
                "    My best guess: you wanted to define {class_}\n"
                "    but forgot to add a colon ':' at the end\n"
                "\n"
            ).format(class_=name)
        elif name in ["for", "while"]:
            return _(
                "    My best guess: you wrote a '{name}' loop but\n"
                "    forgot to add a colon ':' at the end\n"
                "\n"
            ).format(name=name)
        else:
            return _(
                "    My best guess: you wrote a statement beginning with\n"
                "    '{name}' but forgot to add a colon ':' at the end\n"
                "\n"
            ).format(name=name)

    if cause == "malformed def":
        name = _("a function or method")
        return _(
            "    My best guess: you tried to define {class_or_function}\n"
            "    and did not use the correct syntax.\n"
            "    The correct syntax is:\n"
            "        def name ( optional_arguments ):"
            "\n"
        ).format(class_or_function=name)

    if cause.startswith("can't assign to literal"):
        name = cause.replace("can't assign to literal", "").strip()
        return _(
            "    My best guess: you wrote an expression like\n"
            "        {name} = something\n"
            "    where <{name}>, on the left hand-side of the equal sign, is\n"
            "    an actual number or string (what Python calls a 'literal'),\n"
            "    and not the name of a variable.  Perhaps you meant to write:\n"
            "        something = {name}\n"
            "\n"
        ).format(name=name)

    return _(
        "    Currently, we cannot guess the likely cause of this error.\n"
        "    You might want to report this case to\n"
        "    https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
        "    Try to examine closely the line indicated as well as the line\n"
        "    immediately above to see if you can identify some misspelled\n"
        "    word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
    )
