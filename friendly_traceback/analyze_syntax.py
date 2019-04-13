"""analyze_syntax.py

Attempts to find the cause of a SyntaxError.
"""

# Note: we do not attempt to translate strings here,
# so that we can test it. Note that we have not created
# separate unit tests yet - which we really should do.

import keyword
import tokenize
from io import StringIO


class Token:  # Likely overkill
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line


def find_likely_cause(source, linenumber, offset):
    offending_line = source[linenumber - 1].rstrip()

    tokens = []

    try:
        for tok in tokenize.generate_tokens(StringIO(offending_line).readline):
            token = Token(tok)
            if not token.string.strip():  # ignore spaces
                continue
            tokens.append([token.type, token.string])
    except Exception as e:
        return "%s raised while analyzing a SyntaxError" % repr(e)

    for possible in possible_causes:
        cause = possible(tokens)
        if cause:
            return cause

    return "No cause found."


def assign_to_a_keyword(tokens):
    # needs unit tests
    if len(tokens) < 2:
        return False
    _, name = tokens[0]
    _, op = tokens[1]
    if name in keyword.kwlist and op == "=":
        return "Assigning to Python keyword"
    return False


def missing_colon(tokens):
    # needs unit tests:
    if len(tokens) < 2:
        return False
    _, name = tokens[0]
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
        t, last = tokens[-1]
        print("last = ", repr(last), t == tokenize.COMMENT)
        if last != ":":
            return "%s missing colon" % name
    return False


possible_causes = [assign_to_a_keyword, missing_colon]
