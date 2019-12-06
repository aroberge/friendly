import sys

import friendly_traceback

friendly_traceback.set_lang("en")

# We use a dict with indices instead of a list to make it easier to
# figure out quickly which cause correspond to which test case.
causes = {
    1: "assign a value to the Python keyword 'def'",
    2: "'if' but forgot to add a colon ':'",
    3: "wrote a 'while' loop but",
    4: "wrote 'else if' instead",
    5: "wrote 'elseif' instead",
    6: "tried to define a function or method",
    7: "tried to define a function or method",
    8: "tried to define a function or method",
    9: "what Python calls a 'literal'",
    '9a': "what Python calls a 'literal'",
    10: "from turtle import pen",
    11: "EOL while scanning string literal",
    12: "None is a constant in Python",
    13: "__debug__ is a constant in Python",
    14: "The closing parenthesis ')' on",
    15: "The opening parenthesis '(' on line",
    '15a': "The opening parenthesis '(' on line",
    16: "The closing square bracket ']' on line",
    '16a': "The closing square bracket ']' on line",
    17: "In older version of Python, 'print' was a keyword",
    18: "You tried to use the Python keyword",
    19: "The Python keyword 'break' can only be used",
    20: "The Python keyword 'continue' can only be used",
    21: "quote inside a string",
    22: "forgot a comma",
    23: "forgot a comma",
    24: "forgot a comma",
    25: "forgot a comma",
    26: "forgot a comma",
    27: "function call and is not simply the name of a variable",
    28: "function call and not the name of a variable",
    29: "used an equal sign '=' instead of a colon ':'",
    30: "define functions with only positional arguments",
    31: "call functions with only positional arguments",
    32: "a string prefixed by the letter f,",
    33: "The opening square bracket '['",
    34: "The opening square bracket '['",
    35: "is a variable defined outside a function.",
    36: "keyword pass as an attribute",
    37: "using the continuation character",
    38: "where 'invalid' is not a valid variable name in Python",
    39: "as part of a variable name in Python",
    40: "as an argument in the definition of a function",
    41: "as an argument in the definition of a function",
    42: "as an argument in the definition of a function",
    43: "as an argument in the definition of a function",
}

if sys.version_info < (3, 8):
    causes["_walrus"] = "walrus operator"


def test_syntax_errors():
    for i in causes:
        cause = causes[i]
        try:
            exec("from . import raise_syntax_error%s" % i)
        except Exception:
            friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "SyntaxError" in result, "SyntaxError identified incorrectly; %s" % i
        assert cause in result, "\nExpected: %s\nGot: %s" % (cause, result)


if __name__ == "__main__":
    print("Can only run with pytest")
