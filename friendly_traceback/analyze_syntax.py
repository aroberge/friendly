"""analyze_syntax.py

Attempts to find the cause of a SyntaxError.
"""

# Note: we do not attempt to translate strings here,
# so that we can test it. Note that we have not created
# separate unit tests yet - which we really should do.

import keyword
import tokenize
from io import StringIO


possible_causes = []


def add_cause(func):
    possible_causes.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line


def find_likely_cause(source, linenumber, message, offset):

    offending_line = source[linenumber - 1]
    line = offending_line.rstrip()

    if message == "can't assign to literal":
        return assign_to_literal(message, line)

    return analyze_last_line(line)


def assign_to_literal(message, line):
    variable = line.split("=")[0].strip()
    return message + " %s" % variable


def analyze_last_line(line):
    tokens = []
    try:
        for tok in tokenize.generate_tokens(StringIO(line).readline):
            token = Token(tok)
            if not token.string.strip():  # ignore spaces
                continue
            if token.type == tokenize.COMMENT:
                continue
            tokens.append(token)
    except Exception as e:
        return "%s raised while analyzing a SyntaxError" % repr(e)

    for possible in possible_causes:
        if tokens:
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
