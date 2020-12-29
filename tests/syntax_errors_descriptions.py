"""In this file, descriptions is a dict whose keys are the names of
Python files that raise a SyntaxError (or subclass) when they are imported.

"cause" is some text that should be found in the explanation provided by
        Friendly-traceback when importing this file.

"title" is the heading that should appear in the documentation for
        this particular case.
"""

cause = "cause"
title = "title"

descriptions = {
    "raise_indentation_error1": {
        cause: "expected to begin a new indented block",
        title: "IndentationError - 1: expected an indented block",
    },
    "raise_indentation_error2": {
        cause: "does not match the indentation of the previous line",
        title: "IndentationError - 2: unexpected indent",
    },
    "raise_indentation_error3": {
        cause: "not aligned vertically with another block of code",
        title: "IndentationError - 3: unindent does not match ...",
    },
    "raise_tab_error": {
        cause: "A `TabError` indicates that you have used",
        title: "TabError",
    },
    "raise_syntax_error1": {
        cause: "assign a value to the Python keyword `def`",
        title: "SyntaxError - Assign to keyword",
    },
    "raise_syntax_error2": {
        cause: "`if` but forgot to add a colon `:`",
        title: "SyntaxError - Missing colon - 1",
    },
    "raise_syntax_error3": {
        cause: "wrote a `while` loop but",
        title: "SyntaxError - Missing colon - 2",
    },
    "raise_syntax_error4": {
        cause: "wrote `else if` instead",
        title: "SyntaxError - elif, not else if",
    },
    "raise_syntax_error5": {
        cause: "wrote `elseif` instead",
        title: "SyntaxError - elif, not elseif",
    },
    "raise_syntax_error6": {
        cause: "tried to define a function or method",
        title: "SyntaxError - malformed def statment - 1",
    },
    "raise_syntax_error7": {
        cause: "tried to define a function or method",
        title: "SyntaxError - malformed def statment - 2",
    },
    "raise_syntax_error8": {
        cause: "tried to define a function or method",
        title: "SyntaxError - malformed def statment - 3",
    },
    "raise_syntax_error9": {
        cause: "is or includes an actual object of type `int`",
        title: "SyntaxError - can't assign to literal - 1",
    },
    "raise_syntax_error10": {
        cause: "is or includes an actual object of type `int`",
        title: "SyntaxError - can't assign to literal - 2",
    },
    "raise_syntax_error11": {
        cause: "from turtle import pen",
        title: "SyntaxError - import X from Y",
    },
    "raise_syntax_error12": {
        cause: "EOL while scanning string literal",
        title: "SyntaxError - EOL while scanning string literal",
    },
    "raise_syntax_error13": {
        cause: "`None` is a constant in Python",
        title: "SyntaxError - assignment to keyword (None)",
    },
    "raise_syntax_error14": {
        cause: "`__debug__` is a constant in Python",
        title: "SyntaxError - assignment to keyword (__debug__)",
    },
    "raise_syntax_error15": {
        cause: "The closing parenthesis `)` on",
        title: "SyntaxError - unmatched closing parenthesis",
    },
    "raise_syntax_error16": {
        cause: "The opening parenthesis `(` on line",
        title: "SyntaxError - unclosed parenthesis- 1",
    },
    "raise_syntax_error17": {
        cause: "The opening parenthesis `(` on line",
        title: "SyntaxError - unclosed parenthesis - 2",
    },
    "raise_syntax_error18": {
        cause: "The closing square bracket `]` on line",
        title: "SyntaxError - mismatched brackets",
    },
    "raise_syntax_error19": {
        cause: "The closing square bracket `]` on line",
        title: "SyntaxError - mismatched brackets - 2",
    },
    "raise_syntax_error20": {
        cause: "In older version of Python, `print` was a keyword",
        title: "SyntaxError - print is a function",
    },
    "raise_syntax_error21": {
        cause: "You tried to use the Python keyword",
        title: "SyntaxError - Python keyword as function name",
    },
    "raise_syntax_error22": {
        cause: "The Python keyword `break` can only be used",
        title: "SyntaxError - break outside loop",
    },
    "raise_syntax_error23": {
        cause: "The Python keyword `continue` can only be used",
        title: "SyntaxError - continue outside loop",
    },
    "raise_syntax_error24": {
        cause: "quote inside a string",
        title: "SyntaxError - quote inside a string",
    },
    "raise_syntax_error25": {
        cause: "forgot a comma",
        title: "SyntaxError - missing comma in a dict",
    },
    "raise_syntax_error26": {
        cause: "forgot a comma",
        title: "SyntaxError - missing comma in a set",
    },
    "raise_syntax_error27": {
        cause: "forgot a comma",
        title: "SyntaxError - missing comma in a list",
    },
    "raise_syntax_error28": {
        cause: "forgot a comma",
        title: "SyntaxError - missing comma in a tuple",
    },
    "raise_syntax_error29": {
        cause: "forgot a comma",
        title: "SyntaxError - missing comma between function args",
    },
    "raise_syntax_error30": {
        cause: "function call and is not simply the name of a variable",
        title: "SyntaxError - can't assign to function call - 1",
    },
    "raise_syntax_error31": {
        cause: "function call and not the name of a variable",
        title: "SyntaxError - can't assign to function call - 2",
    },
    "raise_syntax_error32": {
        cause: "used an equal sign `=` instead of a colon `:`",
        title: "SyntaxError - used equal sign instead of colon",
    },
    "raise_syntax_error33": {
        cause: "define functions with only positional arguments",
        title: "SyntaxError - non-default argument follows default argument",
    },
    "raise_syntax_error34": {
        cause: "call functions with only positional arguments",
        title: "SyntaxError - positional argument follows keyword argument",
    },
    "raise_syntax_error35": {
        cause: "a string prefixed by the letter f,",
        title: "SyntaxError - f-string: unterminated string",
    },
    "raise_syntax_error36": {
        cause: "The opening square bracket `[`",
        title: "SyntaxError - unclosed bracket",
    },
    "raise_syntax_error37": {
        cause: "The opening square bracket `[`",
        title: "SyntaxError - unexpected EOF while parsing",
    },
    "raise_syntax_error38": {
        cause: "is a variable defined outside a function.",
        title: "SyntaxError - name is parameter and global",
    },
    "raise_syntax_error39": {
        cause: "keyword `pass` as an attribute",
        title: "SyntaxError - keyword as attribute",
    },
    "raise_syntax_error40": {
        cause: "using the continuation character",
        title: "SyntaxError - content passed continuation line character",
    },
    "raise_syntax_error41": {
        cause: "where `invalid` is not a valid variable name in Python",
        title: "SyntaxError - keyword can't be an expression",
    },
    "raise_syntax_error42": {
        cause: "unicode character",
        title: "SyntaxError - invalid character in identifier",
    },
    "raise_syntax_error43": {
        cause: "as an argument in the definition of a function",
        title: "SyntaxError - keyword cannot be argument in def - 1",
    },
    "raise_syntax_error44": {
        cause: "as an argument in the definition of a function",
        title: "SyntaxError - keyword cannot be argument in def - 2",
    },
    "raise_syntax_error45": {
        cause: "as an argument in the definition of a function",
        title: "SyntaxError - keyword cannot be argument in def - 3",
    },
    "raise_syntax_error46": {
        cause: "as an argument in the definition of a function",
        title: "SyntaxError - keyword cannot be argument in def - 4",
    },
    "raise_syntax_error47": {
        cause: "instead of deleting the function's name",
        title: "SyntaxError - delete function call",
    },
    "raise_syntax_error48": {
        cause: "before declaring it as a global variable.",
        title: "SyntaxError - assigned prior to global declaration",
    },
    "raise_syntax_error49": {
        cause: "You used the variable `r`",
        title: "SyntaxError - used prior to global declaration",
    },
    "raise_syntax_error50": {
        cause: "before declaring it as a nonlocal variable.",
        title: "SyntaxError - assigned prior to nonlocal declaration",
    },
    "raise_syntax_error51": {
        cause: "You assigned a value to the variable `s`",
        title: "SyntaxError - used prior to nonlocal declaration",
    },
    "raise_syntax_error52": {
        cause: "is or includes an actual object of type `set`",
        title: "SyntaxError - can't assign to literal - 3",
    },
    "raise_syntax_error53": {
        cause: "is or includes an actual object of type `dict`",
        title: "SyntaxError - can't assign to literal - 4",
    },
    "raise_syntax_error54": {
        cause: "is or includes an actual object",
        title: "SyntaxError - can't assign to literal - 5",
    },
    "raise_syntax_error55": {  # May differ depending on Python version
        cause: "`True` is a constant in Python",
        title: "SyntaxError - named assignment with Python constant",
    },
    "raise_syntax_error56": {
        cause: "only used to assign a value to a variable",
        title: "SyntaxError - named assignment with Python constant",
    },
    "raise_syntax_error57": {
        cause: "use the function `repr(x)`.",
        title: "SyntaxError - using the backquote character",
    },
    "raise_syntax_error58": {
        cause: "generator expression instead of the name of a variable",
        title: "SyntaxError - assign to generator expression",
    },
    "raise_syntax_error59": {
        cause: "variable = object if condition else other_object",
        title: "SyntaxError - assign to conditional expression",
    },
    "raise_syntax_error60": {
        cause: "You used `x` as a parameter for a function",
        title: "SyntaxError - name is parameter and nonlocal",
    },
    "raise_syntax_error61": {
        cause: "You declared `xy` as being both a global and nonlocal",
        title: "SyntaxError - name is global and nonlocal",
    },
    "raise_syntax_error62": {
        cause: "nonlocal variable but it cannot be found.",
        title: "SyntaxError - nonlocal variable not found",
    },
    "raise_syntax_error63": {
        cause: "You used the nonlocal keyword at a module level",
        title: "SyntaxError - nonlocal variable not found at module level",
    },
    "raise_syntax_error64": {
        cause: "keyword argument should appear only once in a function definition",
        title: "SyntaxError - keyword arg only once in function definition",
    },
    "raise_syntax_error65": {
        cause: "keyword argument should appear only once in a function call",
        title: "SyntaxError - keyword arg only once in function call",
    },
    "raise_syntax_error66": {  # May differ depending on Python version
        cause: "it reached the end of the file and expected more content.",
        title: "SyntaxError - unexpected EOF while parsing 2",
    },
    "raise_syntax_error67": {
        cause: "In older version of Python, `print` was a keyword",
        title: "SyntaxError - print is a function 2",
    },
    "raise_syntax_error68": {
        cause: "copy-pasted code from an interactive interpreter",
        title: "SyntaxError - copy/paste from interpreter",
    },
    "raise_syntax_error69": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "SyntaxError - Using pip from interpreter",
    },
    "raise_syntax_error70": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "SyntaxError - Using pip from interpreter 2",
    },
    "raise_syntax_error71": {
        cause: "dot `.` followed by `(`",
        title: "SyntaxError - dot followed by parenthesis",
    },
    "raise_syntax_error72": {
        cause: "expression that has an f-string",
        title: "SyntaxError - cannot assign to f-string",
    },
    "raise_syntax_error73": {
        cause: "trying to raise an exception using Python 2 syntax.",
        title: "SyntaxError - raising multiple exceptions",
    },
    "raise_syntax_error74": {
        cause: "must add parentheses enclosing",
        title: "SyntaxError - parenthesis around generator expression",
    },
    "raise_syntax_error75": {
        cause: "fancy unicode quotation mark",
        title: "SyntaxError - invalid character (bad quote)",
    },
    "raise_syntax_error76": {
        cause: "`=` instead of an equality operator `==` with an `if` statement",
        title: "SyntaxError - single = instead of double == with if",
    },
    "raise_syntax_error77": {
        cause: "`=` instead of an equality operator `==` with an `elif` statement",
        title: "SyntaxError - single = instead of double == with elif",
    },
    "raise_syntax_error78": {
        cause: "You used an assignment operator `=`",
        title: "SyntaxError - single = instead of double == with while",
    },
    "raise_syntax_error79": {
        cause: "forgot a comma",
        title: "SyntaxError - forgot a comma in an f-string",
    },
    "raise_syntax_error80": {
        cause: "Valid names cannot begin with a number",
        title: "SyntaxError - Valid names cannot begin with a number",
    },
    "raise_syntax_error81": {
        cause: "The opening parenthesis `(` on line 5 is not closed",
        title: "SyntaxError - unclosed parenthesis - 3",
    },
    "raise_syntax_error82": {
        cause: "Perhaps you forgot a multiplication operator",
        title: "SyntaxError - forgot a multiplication operator",
    },
    "raise_syntax_error83": {
        cause: "Did you mean `a_b`",
        title: "SyntaxError - space between names",
    },
    "raise_syntax_error84": {
        cause: "The star operator",
        title: "SyntaxError - can't use star operator",
    },
    "raise_syntax_error85": {
        cause: "The double star operator",
        title: "SyntaxError - can't use double star operator",
    },
    "raise_syntax_error86": {
        cause: "You can only use a `return`",
        title: "SyntaxError - can't use return outside function",
    },
    "raise_syntax_error87": {
        cause: "Seriously",
        title: "SyntaxError - too many nested blocks",
    },
    "raise_syntax_error88": {
        cause: "replace `*` by either `*arguments` or ",
        title: "SyntaxError - named arguments must follow bare *",
    },
    "raise_syntax_error89": {cause: "Did you mean `3.0 j`", title: "SyntaxError - use j instead of i"},
    "raise_syntax_error90": {
        cause: "you must import specific named features",
        title: "SyntaxError - do not import * from __future__",
    },
    "raise_syntax_error91": {cause: "Did you mean `division`", title: "SyntaxError - typo in __future__"},
    "raise_syntax_error92": {cause: "print_function", title: "SyntaxError - unkown feature in __future__"},
    "raise_syntax_error93": {cause: "from __future__ import braces", title: "SyntaxError - Not a chance!"},
    "raise_syntax_error94": {
        cause: "It must appear at the beginning of the file.",
        title: "SyntaxError - __future__ at beginning",
    },
}
