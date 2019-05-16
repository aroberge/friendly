"""analyze_syntax.py

Attempts to find the most likely cause of a SyntaxError.
"""

import keyword
import tokenize

from .my_gettext import current_lang
from . import utils

PYTHON_MESSAGES = []
LINE_ANALYZERS = []


def find_likely_cause(etype, value):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    partial_source, _ignore = utils.get_partial_source(filepath, linenumber, offset)
    source = utils.get_source(filepath)
    return _find_likely_cause(source, linenumber, message, offset)


def _find_likely_cause(source, linenumber, message, offset):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    _ = current_lang.translate

    offending_line = source[linenumber - 1]
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides.
    for case in PYTHON_MESSAGES:
        cause = case(message=message, line=line)
        if cause:
            return cause

    # If not cause has been identified, we look at a single line
    # where the error has been found by Python, and try to find the source
    # of the error

    cause = analyze_last_line(line)
    if cause:
        return cause

    # Eventually, we might add another step that looks at the entire code
    # For now, we just stop here
    return _(
        "Currently, we cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "You might want to report this case to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
    )


def add_python_message(func):
    """A simple decorator that adds a function the the list of functions
       that process a message given by Python.
    """
    PYTHON_MESSAGES.append(func)

    def wrapper(**kwargs):
        return func(**kwargs)

    return wrapper


@add_python_message
def assign_to_literal(message=None, line=None, **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to literal"  # Python 3.6, 3.7
        or message == "cannot assign to literal"  # Python 3.8
    ):
        info = line.split("=")
        literal = info[0].strip()
        name = info[1].strip()

        return _(
            "You wrote an expression like\n"
            "    {literal} = {name}\n"
            "where <{literal}>, on the left hand-side of the equal sign, is\n"
            "an actual number or string (what Python calls a 'literal'),\n"
            "and not the name of a variable. Perhaps you meant to write:\n"
            "    {name} = {literal}\n"
            "\n"
        ).format(literal=literal, name=name)


@add_python_message
def eol_while_scanning_string_literal(message=None, **kwargs):
    _ = current_lang.translate
    if "EOL while scanning string literal" in message:
        return _(
            "You starting writing a string with a single or double quote\n"
            "but never ended the string with another quote on that line.\n"
        )


# ==================
# End of analysis of messages
# ==================


def analyze_last_line(line):
    """Analyzes the last line of code as identified by Python as that
       on which the error occurred."""
    tokens = utils.collect_tokens(line)  # tokens do not include spaces nor comments

    if not tokens:
        return None

    for analyzer in LINE_ANALYZERS:
        cause = analyzer(tokens)
        if cause:
            return cause
    return None


def add_line_analyzer(func):
    """A simple decorator that adds a function to the list
       of all functions that analyze a single line of code."""
    LINE_ANALYZERS.append(func)

    def wrapper(line):
        return func(line)

    return wrapper


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order can yield incorrect results
# ==================


@add_line_analyzer
def assign_to_a_keyword(tokens):
    """Checks to see if line is of the form 'keyword = ...'
    """
    _ = current_lang.translate
    if (
        len(tokens) < 2
        or (tokens[0].string not in keyword.kwlist)
        or tokens[1].string != "="
    ):
        return False

    return _(
        "You were trying to assign a value to the Python keyword '{keyword}'.\n"
        "This is not allowed.\n"
        "\n"
    ).format(keyword=tokens[0].string)


@add_line_analyzer
def confused_elif(tokens):
    _ = current_lang.translate
    name = None
    if tokens[0].string == "elseif":
        name = "elseif"
    elif tokens[0].string == "else" and len(tokens) > 1 and tokens[1].string == "if":
        name = "else if"
    if name:
        return _(
            "You meant to use Python's 'elif' keyword\n"
            "but wrote '{name}' instead\n"
            "\n"
        ).format(name=name)


@add_line_analyzer
def import_from(tokens):
    _ = current_lang.translate
    if len(tokens) < 4:
        return
    if tokens[0].string != "import":
        return
    third = tokens[2].string
    if third == "from":
        function = tokens[1].string
        module = tokens[3].string

        return _(
            "You wrote something like\n"
            "    import {function} from {module}\n"
            "instead of\n"
            "    from {module} import {function}\n"
            "\n"
        ).format(module=module, function=function)


@add_line_analyzer
def missing_colon(tokens):
    """look for missing colon at the end of a line of code"""
    _ = current_lang.translate

    if tokens[-1].string == ":":
        return None

    name = tokens[0].string

    if name == "class":
        name = _("a class")
        return _(
            "You wanted to define {class_}\n"
            "but forgot to add a colon ':' at the end\n"
            "\n"
        ).format(class_=name)
    elif name in ["for", "while"]:
        return _(
            "You wrote a '{for_while}' loop but\n"
            "forgot to add a colon ':' at the end\n"
            "\n"
        ).format(for_while=name)
    elif name in ["def", "elif", "else", "except", "finally", "if", "try"]:
        return _(
            "You wrote a statement beginning with\n"
            "'{name}' but forgot to add a colon ':' at the end\n"
            "\n"
        ).format(name=name)


@add_line_analyzer
def malformed_def(tokens):
    # need at least five tokens: def name ( ) :
    _ = current_lang.translate
    if tokens[0].string != "def":
        return False

    if (
        len(tokens) < 5
        or tokens[1].type != tokenize.NAME
        or tokens[2].string != "("
        or tokens[-2].string != ")"
        or tokens[-1].string != ":"
    ):
        name = _("a function or method")
        return _(
            "You tried to define {class_or_function}\n"
            "and did not use the correct syntax.\n"
            "The correct syntax is:\n"
            "    def name ( optional_arguments ):"
            "\n"
        ).format(class_or_function=name)
