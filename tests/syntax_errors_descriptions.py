"""In this file, descriptions is a dict whose keys are the names of
Python files that raise a SyntaxError (or subclass) when they are imported.

"cause" is some text that should be found in the explanation provided by
        Friendly-traceback when importing this file.

"title" is the heading that should appear in the documentation for
        this particular case.
"""
import sys

cause = "cause"
title = "title"

descriptions = {
    "raise_indentation_error1": {
        cause: "expected to begin a new indented block",
        title: "IndentationError: expected an indented block",
    },
    "raise_indentation_error2": {
        cause: "is more indented than expected",
        title: "IndentationError: unexpected indent",
    },
    "raise_indentation_error3": {
        cause: "is less indented than expected",
        title: "IndentationError: unindent does not match ...",
    },
    "raise_indentation_error4": {
        cause: "meant to include a continuation character",
        title: "IndentationError: missing continuation line",
    },
    "raise_tab_error": {
        cause: "A `TabError` indicates that you have used",
        title: "TabError",
    },
    "raise_syntax_error0": {  # else is flagged
        cause: "assign a value to the Python keyword `else`",
        title: "Assign to keyword",
    },
    "raise_syntax_error1": {  # = sign is flagged
        cause: "assign a value to the Python keyword `def`",
        title: "Assign to keyword",
    },
    "raise_syntax_error2": {
        cause: "`if` but forgot to add a colon `:`",
        title: "Missing colon - if",
    },
    "raise_syntax_error3": {
        cause: "wrote a `while` loop but",
        title: "Missing colon - while",
    },
    "raise_syntax_error4": {
        cause: "wrote `else if` instead",
        title: "Write elif, not else if",
    },
    "raise_syntax_error5": {
        cause: "wrote `elseif` instead",
        title: "Write elif, not elseif",
    },
    "raise_syntax_error6": {
        cause: "tried to define a function",
        title: "Malformed def statement - 1",
    },
    "raise_syntax_error7": {
        cause: "Did you forget parentheses?",
        title: "Malformed def statement - missing parentheses",
    },
    "raise_syntax_error8": {
        cause: "forgot to name your function",
        title: "Malformed def statement - 3",
    },
    "raise_syntax_error9": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal - 1",
    },
    "raise_syntax_error10": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal - 2",
    },
    "raise_syntax_error11": {
        cause: "from turtle import pen",
        title: "Inversion: import X from Y",
    },
    "raise_syntax_error12": {
        cause: "ended the string with another quote",
        title: "EOL while scanning string literal",
    },
    "raise_syntax_error13": {
        cause: "`None` is a constant in Python",
        title: "Assignment to keyword (None)",
    },
    "raise_syntax_error14": {
        cause: "`__debug__` is a constant in Python",
        title: "Assignment to keyword (__debug__)",
    },
    "raise_syntax_error15": {
        cause: "The closing parenthesis `)` on",
        title: "Unmatched closing parenthesis",
    },
    "raise_syntax_error16": {
        cause: "The opening parenthesis `(` on line",
        title: "Unclosed parenthesis - 1",
    },
    "raise_syntax_error17": {
        cause: "The opening parenthesis `(` on line",
        title: "Unclosed parenthesis - 2",
    },
    "raise_syntax_error18": {
        cause: "The closing square bracket `]` on line",
        title: "Mismatched brackets - 1",
    },
    "raise_syntax_error19": {
        cause: "The closing square bracket `]` on line",
        title: "Mismatched brackets - 2",
    },
    "raise_syntax_error20": {
        cause: "In older version of Python, `print` was a keyword",
        title: "print is a function",
    },
    "raise_syntax_error21": {
        cause: "You tried to use the Python keyword",
        title: "Python keyword as function name",
    },
    "raise_syntax_error22": {
        cause: "The Python keyword `break` can only be used",
        title: "break outside loop",
    },
    "raise_syntax_error23": {
        cause: "The Python keyword `continue` can only be used",
        title: "continue outside loop",
    },
    "raise_syntax_error24": {
        cause: "quote inside a string",
        title: "Quote inside a string",
    },
    "raise_syntax_error25": {
        cause: "forgot a comma",
        title: "Missing comma in a dict",
    },
    "raise_syntax_error26": {
        cause: "The following lines of code",
        title: "Missing comma in a set",
    },
    "raise_syntax_error27": {
        cause: "The following lines of code",
        title: "Missing comma in a list",
    },
    "raise_syntax_error28": {
        cause: "The following lines of code",
        title: "Missing comma in a tuple",
    },
    "raise_syntax_error29": {
        cause: "Did you forget a comma",
        title: "Missing comma between function args",
    },
    "raise_syntax_error30": {
        cause: "function call and is not simply the name of a variable",
        title: "Cannot assign to function call - 1",
    },
    "raise_syntax_error31": {
        cause: "function call and not the name of a variable",
        title: "Cannot assign to function call - 2",
    },
    "raise_syntax_error32": {
        cause: "used an equal sign `=` instead of a colon `:`",
        title: "Used equal sign instead of colon",
    },
    "raise_syntax_error33": {
        cause: "define functions with only positional arguments",
        title: "Non-default argument follows default argument",
    },
    "raise_syntax_error34": {
        cause: "call functions with only positional arguments",
        title: "Positional argument follows keyword argument",
    },
    "raise_syntax_error35": {
        cause: "you have another string, which starts with either",
        title: "f-string: unterminated string",
    },
    "raise_syntax_error36": {
        cause: "The opening square bracket `[`",
        title: "Unclosed bracket",
    },
    "raise_syntax_error37": {
        cause: "The opening square bracket `[`",
        title: "Unexpected EOF while parsing",
    },
    "raise_syntax_error38": {
        cause: "is a variable defined outside a function.",
        title: "Name is parameter and global",
    },
    "raise_syntax_error39": {
        cause: "keyword `pass` as an attribute",
        title: "Keyword as attribute",
    },
    "raise_syntax_error40": {
        cause: "using the continuation character",
        title: "Content passed continuation line character",
    },
    "raise_syntax_error41": {
        cause: "where `invalid` is not a valid variable name in Python",
        title: "Keyword can't be an expression",
    },
    "raise_syntax_error42": {
        cause: "unicode character",
        title: "Invalid character in identifier",
    },
    "raise_syntax_error43": {
        cause: "as an argument in the definition of a function",
        title: "Keyword cannot be argument in def - 1",
    },
    "raise_syntax_error44": {
        cause: "as an argument in the definition of a function",
        title: "Keyword cannot be argument in def - 2",
    },
    "raise_syntax_error45": {
        cause: "as an argument in the definition of a function",
        title: "Keyword cannot be argument in def - 3",
    },
    "raise_syntax_error46": {
        cause: "as an argument in the definition of a function",
        title: "Keyword cannot be argument in def - 4",
    },
    "raise_syntax_error47": {
        cause: "instead of deleting the function's name",
        title: "Delete function call",
    },
    "raise_syntax_error48": {
        cause: "before declaring it as a global variable.",
        title: "Name assigned prior to global declaration",
    },
    "raise_syntax_error49": {
        cause: "You used the variable `r`",
        title: "Name used prior to global declaration",
    },
    "raise_syntax_error50": {
        cause: "before declaring it as a nonlocal variable.",
        title: "Name used prior to nonlocal declaration",
    },
    "raise_syntax_error51": {
        cause: "You assigned a value to the variable `s`",
        title: "Name assigned prior to nonlocal declaration",
    },
    "raise_syntax_error52": {
        cause: "is or includes an actual object of type `set`",
        title: "Cannot assign to literal - 3",
    },
    "raise_syntax_error53": {
        cause: "is or includes an actual object of type `dict`",
        title: "Cannot assign to literal - 4",
    },
    "raise_syntax_error54": {
        cause: "is or includes an actual object",
        title: "Cannot assign to literal - 5",
    },
    "raise_syntax_error55": {  # May differ depending on Python version
        cause: "`True` is a constant in Python",
        title: "Walrus/Named assignment depending on Python version",
    },
    "raise_syntax_error56": {
        cause: "only used to assign a value to a variable",
        title: "Named assignment with Python constant",
    },
    "raise_syntax_error57": {
        cause: "use the function `repr(x)`.",
        title: "Using the backquote character",
    },
    "raise_syntax_error58": {
        cause: "generator expression instead of the name of a variable",
        title: "Assign to generator expression",
    },
    "raise_syntax_error59": {
        cause: "variable = object if condition else other_object",
        title: "Assign to conditional expression",
    },
    "raise_syntax_error60": {
        cause: "You used `x` as a parameter for a function",
        title: "Name is parameter and nonlocal",
    },
    "raise_syntax_error61": {
        cause: "You declared `xy` as being both a global and nonlocal",
        title: "Name is global and nonlocal",
    },
    "raise_syntax_error62": {
        cause: "nonlocal variable but it cannot be found.",
        title: "nonlocal variable not found",
    },
    "raise_syntax_error63": {
        cause: "You used the nonlocal keyword at a module level",
        title: "nonlocal variable not found at module level",
    },
    "raise_syntax_error64": {
        cause: "keyword argument should appear only once in a function definition",
        title: "Keyword arg only once in function definition",
    },
    "raise_syntax_error65": {
        cause: "keyword argument should appear only once in a function call",
        title: "Keyword arg only once in function call",
    },
    "raise_syntax_error66": {  # May differ depending on Python version
        cause: "it reached the end of the file and expected more content.",
        title: "IndentationError/SyntaxError depending on version",
    },
    "raise_syntax_error67": {
        cause: "In older version of Python, `print` was a keyword",
        title: "print is a function 2",
    },
    "raise_syntax_error68": {
        cause: "copy-pasted code from an interactive interpreter",
        title: "Copy/paste from interpreter",
    },
    "raise_syntax_error69": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "Using pip from interpreter",
    },
    "raise_syntax_error70": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "Using pip from interpreter 2",
    },
    "raise_syntax_error71": {
        cause: "dot `.` followed by `(`",
        title: "Dot followed by parenthesis",
    },
    "raise_syntax_error72": {
        cause: "expression that has the f-string",
        title: "Cannot assign to f-string",
    },
    "raise_syntax_error73": {
        cause: "trying to raise an exception using Python 2 syntax.",
        title: "Raising multiple exceptions",
    },
    "raise_syntax_error74": {
        cause: "must add parentheses enclosing",
        title: "Parenthesis around generator expression",
    },
    "raise_syntax_error75": {
        cause: "fancy unicode quotation mark",
        title: "Invalid character (bad quote)",
    },
    "raise_syntax_error76": {
        cause: "You used an assignment operator `=`",
        title: "Single = instead of double == with if",
    },
    "raise_syntax_error77": {
        cause: "You used an assignment operator `=`",
        title: "Single = instead of double == with elif",
    },
    "raise_syntax_error78": {
        cause: "You used an assignment operator `=`",
        title: "Single = instead of double == with while",
    },
    "raise_syntax_error79": {
        cause: "Did you made a mistake in writing an hexadecimal integer",
        title: "Invalid hexadecimal number",
    },
    "raise_syntax_error80": {
        cause: "Valid names cannot begin with a number",
        title: "Valid names cannot begin with a number",
    },
    "raise_syntax_error81": {
        cause: "The opening parenthesis `(` on line 5 is not closed",
        title: "Unclosed parenthesis - 3",
    },
    "raise_syntax_error82": {
        cause: "Perhaps you forgot a multiplication operator",
        title: "Forgot a multiplication operator",
    },
    "raise_syntax_error83": {
        cause: "Did you mean `a_b`",
        title: "Space between names",
    },
    "raise_syntax_error84": {
        cause: "The star operator",
        title: "Cannot use star operator",
    },
    "raise_syntax_error85": {
        cause: "The double star operator",
        title: "Cannot use double star operator",
    },
    "raise_syntax_error86": {
        cause: "You can only use a `return`",
        title: "Cannot use return outside function",
    },
    "raise_syntax_error87": {
        cause: "Seriously",
        title: "Too many nested blocks",
    },
    "raise_syntax_error88": {
        cause: "replace `*` by either `*arguments` or ",
        title: "Named arguments must follow bare *",
    },
    "raise_syntax_error89": {
        cause: "Did you mean `3.0j`",
        title: "use j instead of i",
    },
    "raise_syntax_error90": {
        cause: "you must import specific named features",
        title: "Do not import * from __future__",
    },
    "raise_syntax_error91": {
        cause: "Did you mean `division`",
        title: "Typo in __future__",
    },
    "raise_syntax_error92": {
        cause: "print_function",
        title: "Unknown feature in __future__",
    },
    "raise_syntax_error93": {
        cause: "from __future__ import braces",
        title: "Not a chance!",
    },
    "raise_syntax_error94": {
        cause: "It must appear at the beginning of the file.",
        title: "__future__ at beginning",
    },
    "raise_syntax_error95": {
        cause: "Did you made a mistake in writing an octal integer",
        title: "Invalid octal number",
    },
    "raise_syntax_error96": {
        cause: "use a string as a function name",
        title: "Using a string as a function name",
    },
    "raise_syntax_error97": {
        cause: "The name of a function must be a valid Python identifier",
        title: "Non-identifier as a function name",
    },
    "raise_syntax_error98": {
        cause: "the exact same object, use the operator `is`",
        title: "Triple-equal sign",
    },
    "raise_syntax_error99": {
        cause: "you forgot that you cannot have spaces",
        title: "Two consecutive names",
    },
    "raise_syntax_error100": {
        cause: "only be used for boolean expressions",
        title: "Using 'and' in import statement",
    },
    "raise_syntax_error101": {
        cause: "It cannot be declared to be a global variable.",
        title: "Annotated name cannot be global",
    },
    "raise_syntax_error102": {
        cause: "you forgot that you cannot have spaces",
        title: "Two consecutive names",
    },
    "raise_syntax_error103": {
        cause: "You cannot delete the constant",
        title: "Deleting constant/keyword",
    },
    "raise_syntax_error104": {
        cause: "You cannot delete the literal",
        title: "Deleting literal",
    },
    "raise_syntax_error105": {
        cause: "Did you forget to escape a backslash character",
        title: "EOL unescaped backslash",
    },
    "raise_syntax_error106": {
        cause: "you can replace the part that contains a backslash",
        title: "f-string with backslash",
    },
}


if sys.version_info < (3, 8):
    descriptions["raise_syntax_error55"]["cause"] = "walrus operator"
    descriptions["raise_syntax_error_walrus"] = {
        cause: "walrus operator",
        title: "Walrus operator does not exist - yet",
    }
    del descriptions["raise_syntax_error99"]
    del descriptions["raise_syntax_error102"]

if sys.version_info >= (3, 9):
    descriptions["raise_syntax_error66"]["cause"] = "expected an indented block"

if sys.version_info >= (3, 10):
    descriptions["raise_syntax_error24"]["cause"] = "ended the string with another quote"
    del descriptions["raise_syntax_error26"]  # Temporary due to a bug in CPython
    del descriptions["raise_syntax_error27"]  # Temporary due to a bug in CPython
