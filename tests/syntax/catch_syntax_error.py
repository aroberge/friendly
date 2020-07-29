import sys

import pytest

import friendly_traceback

friendly_traceback.set_lang("en")

# Format of the dict below
# filename : "partial content of the Friendly traceback information"

causes = {
    "raise_indentation_error1": "expected to begin a new indented block",
    "raise_indentation_error2": "does not match the indentation of the previous line",
    "raise_indentation_error3": "not aligned vertically with another block of code",
    "raise_tab_error": "A TabError indicates that you have used",
    "raise_syntax_error1": "assign a value to the Python keyword 'def'",
    "raise_syntax_error2": "'if' but forgot to add a colon ':'",
    "raise_syntax_error3": "wrote a 'while' loop but",
    "raise_syntax_error4": "wrote 'else if' instead",
    "raise_syntax_error5": "wrote 'elseif' instead",
    "raise_syntax_error6": "tried to define a function or method",
    "raise_syntax_error7": "tried to define a function or method",
    "raise_syntax_error8": "tried to define a function or method",
    "raise_syntax_error9": "is or includes an actual object of type 'int'",
    "raise_syntax_error10": "is or includes an actual object of type 'int'",
    "raise_syntax_error11": "from turtle import pen",
    "raise_syntax_error12": "EOL while scanning string literal",
    "raise_syntax_error13": "None is a constant in Python",
    "raise_syntax_error14": "__debug__ is a constant in Python",
    "raise_syntax_error15": "The closing parenthesis ')' on",
    "raise_syntax_error16": "The opening parenthesis '(' on line",
    "raise_syntax_error17": "The opening parenthesis '(' on line",
    "raise_syntax_error18": "The closing square bracket ']' on line",
    "raise_syntax_error19": "The closing square bracket ']' on line",
    "raise_syntax_error20": "In older version of Python, 'print' was a keyword",
    "raise_syntax_error21": "You tried to use the Python keyword",
    "raise_syntax_error22": "The Python keyword 'break' can only be used",
    "raise_syntax_error23": "The Python keyword 'continue' can only be used",
    "raise_syntax_error24": "quote inside a string",
    "raise_syntax_error25": "forgot a comma",
    "raise_syntax_error26": "forgot a comma",
    "raise_syntax_error27": "forgot a comma",
    "raise_syntax_error28": "forgot a comma",
    "raise_syntax_error29": "forgot a comma",
    "raise_syntax_error30": "function call and is not simply the name of a variable",
    "raise_syntax_error31": "function call and not the name of a variable",
    "raise_syntax_error32": "used an equal sign '=' instead of a colon ':'",
    "raise_syntax_error33": "define functions with only positional arguments",
    "raise_syntax_error34": "call functions with only positional arguments",
    "raise_syntax_error35": "a string prefixed by the letter f,",
    "raise_syntax_error36": "The opening square bracket '['",
    "raise_syntax_error37": "The opening square bracket '['",
    "raise_syntax_error38": "is a variable defined outside a function.",
    "raise_syntax_error39": "keyword pass as an attribute",
    "raise_syntax_error40": "using the continuation character",
    "raise_syntax_error41": "where 'invalid' is not a valid variable name in Python",
    "raise_syntax_error42": "unicode character",
    "raise_syntax_error43": "as an argument in the definition of a function",
    "raise_syntax_error44": "as an argument in the definition of a function",
    "raise_syntax_error45": "as an argument in the definition of a function",
    "raise_syntax_error46": "as an argument in the definition of a function",
    "raise_syntax_error47": "instead of deleting the function's name",
    "raise_syntax_error48": "before declaring it as a global variable.",
    "raise_syntax_error49": "You used the variable 'r'",
    "raise_syntax_error50": "before declaring it as a nonlocal variable.",
    "raise_syntax_error51": "You assigned a value to the variable 's'",
    "raise_syntax_error52": "is or includes an actual object of type 'set'",
    "raise_syntax_error53": "is or includes an actual object of type 'dict'",
    "raise_syntax_error54": "is or includes an actual object",
    "raise_syntax_error55": "True is a constant in Python",
    "raise_syntax_error56": "only used to assign a value to a variable",
    "raise_syntax_error57": "use the function repr(x) instead of `x`.",
    "raise_syntax_error58": "generator expression instead of the name of a variable",
    "raise_syntax_error59": "variable = object if condition else other_object",
    "raise_syntax_error60": "You used 'x' as a parameter for a function",
    "raise_syntax_error61": "You declared 'xy' as being both a global and nonlocal",
    "raise_syntax_error62": "nonlocal variable but it cannot be found.",
    "raise_syntax_error63": "You used the nonlocal keyword at a module level",
    "raise_syntax_error64": "keyword argument should appear only once in a function definition",
    "raise_syntax_error65": "keyword argument should appear only once in a function call",
    "raise_syntax_error66": "it reached the end of the file and expected more content.",
    "raise_syntax_error67": "In older version of Python, 'print' was a keyword",
    "raise_syntax_error68": "copy-pasted code from an interactive interpreter",
    "raise_syntax_error69": "pip is a command that needs to run in a terminal",
    "raise_syntax_error70": "pip is a command that needs to run in a terminal",
    "raise_syntax_error71": "dot '.' followed by (",
    "raise_syntax_error72": "expression that has an f-string",
    "raise_syntax_error73": "trying to raise an exception using Python 2 syntax.",
    "raise_syntax_error74": "must add parentheses enclosing",
    "raise_syntax_error75": "fancy unicode quotation mark",
}

if sys.version_info < (3, 8):
    causes["raise_syntax_error_walrus"] = "walrus operator"
    causes["raise_syntax_error55"] = "walrus operator"
if sys.version_info >= (3, 9):
    causes["raise_syntax_error66"] = "expected an indented block"


@pytest.mark.parametrize("filename", causes.keys())
def test_syntax_errors(filename):
    cause = causes[filename]
    try:
        try:
            exec("from . import %s" % filename)  # for pytest
        except ImportError:
            exec("import %s" % filename)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()

    if "syntax" in filename:
        assert "SyntaxError" in result, (
            "SyntaxError identified incorrectly; %s" % filename
        )
    elif "indentation" in filename:
        assert "IndentationError" in result, (
            "IndentationError identified incorrectly; %s" % filename
        )
    else:
        assert "TabError" in result, "TabError identified incorrectly; %s" % filename
    unwrapped_result = " ".join(result.split())
    assert cause in unwrapped_result, "\nExpected to see: %s\nIn: %s" % (cause, result)
