# see https://github.com/python/cpython/blob/master/Lib/test/test_syntax.py
# for a list of examples with specific messages that should be
# included.

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
    17: "In older version of Python, 'print' was a keyword",
    18: "You tried to use the Python keyword",
    19: "The Python keyword 'break' can only be used",
    20: "The Python keyword 'continue' can only be used",
    21: "quote inside a string",
}


def test_syntax_errors():
    for i in causes:
        cause = causes[i]
        try:
            exec("from . import raise_syntax_error%s" % i)
        except Exception:
            friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "SyntaxError" in result, "SyntaxError identified incorrectly; %s" % i
        assert cause in result, "Cause %s identified incorrectly" % result


if __name__ == "__main__":
    print("Can only run with pytest")
