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
    "assign_to_debug": {
        cause: "`__debug__` is a constant in Python",
        title: "Assignment to keyword (__debug__)",
    },
    "assign_to_keyword_def": {  # = sign is flagged
        cause: "assign a value to the Python keyword `def`",
        title: "Assign to keyword def",
    },
    "assign_to_keyword_else": {  # else is flagged
        cause: "assign a value to the Python keyword `else`",
        title: "Assign to keyword else",
    },
    "assign_to_keyword_none": {
        cause: "`None` is a constant in Python",
        title: "Assignment to keyword (None)",
    },
    "break_outside_loop": {
        cause: "The Python keyword `break` can only be used",
        title: "break outside loop",
    },
    "cannot_assign_to_function_call_1": {
        cause: "function call and is not simply the name of a variable",
        title: "Cannot assign to function call: single = sign",
        "other causes": ["len('a')"],
    },
    "cannot_assign_to_function_call_2": {
        cause: "function call and not the name of a variable",
        title: "Cannot assign to function call: two = signs",
        "other causes": ["func(...)"],
    },
    "cannot_assign_to_literal_int": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal int",
        "other causes": ["Perhaps you meant to write"],
    },
    "cannot_assign_to_literal_int2": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal int - 2",
    },
    "cannot_delete_function_call": {
        cause: "instead of deleting the function's name",
        title: "Cannot delete function call",
    },
    "continue_outside_loop": {
        cause: "The Python keyword `continue` can only be used",
        title: "continue outside loop",
    },
    "def_code_block": {
        cause: "tried to define a function",
        title: "def: misused as code block",
    },
    "def_keyword_as_arg_1": {
        cause: "as an argument in the definition of a function",
        title: "def: keyword cannot be argument in def - 1",
    },
    "def_keyword_as_arg_2": {
        cause: "as an argument in the definition of a function",
        title: "def: keyword cannot be argument in def - 2",
    },
    "def_keyword_as_arg_3": {
        cause: "as an argument in the definition of a function",
        title: "def: keyword cannot be argument in def - 3",
    },
    "def_keyword_as_arg_4": {
        cause: "as an argument in the definition of a function",
        title: "def: keyword cannot be argument in def - 4",
    },
    "def_keyword_as_name": {
        cause: "You tried to use the Python keyword",
        title: "def: Python keyword as function name",
    },
    "def_missing_comma": {
        cause: "Did you forget a comma",
        title: "def: missing comma between function args",
    },
    "def_missing_parens": {
        cause: "Did you forget parentheses?",
        title: "def: missing parentheses",
    },
    "def_missing_name": {
        cause: "forgot to name your function",
        title: "def: missing function name",
    },
    "def_name_is_parameter_and_global": {
        cause: "is a variable defined outside a function.",
        title: "def: name is parameter and global",
    },
    "def_non_default_after_default": {
        cause: "define functions with only positional arguments",
        title: "def: non-default argument follows default argument",
    },
    "def_positional_after_keyword_arg": {
        cause: "call functions with only positional arguments",
        title: "def: positional argument follows keyword argument",
    },
    "def_tuple_as_arg_1":{
        cause: "You cannot have explicit tuples as arguments.",
        title: "def: tuple as function argument"
    },
    "def_tuple_as_arg_2": {
        cause: "You cannot have explicit tuples as arguments.",
        title: "def: tuple as function argument - 2"
    },
    "else_if_instead_of_elif": {
        cause: "wrote `else if` instead",
        title: "Write elif, not else if",
    },
    "elseif_instead_of_elif": {
        cause: "wrote `elseif` instead",
        title: "Write elif, not elseif",
    },
    "eol_string_literal": {
        cause: "ended the string with another quote",
        title: "EOL while scanning string literal",
    },
    "equal_sign_instead_of_colon": {
        cause: "used an equal sign `=` instead of a colon `:`",
        title: "Used equal sign instead of colon",
    },
    "f_string_unterminated": {
        cause: "you have another string, which starts with either",
        title: "f-string: unterminated string",
    },
    "import_from": {
        cause: "from turtle import pen",
        title: "Import inversion: import X from Y",
    },
    "invalid_character_in_identifier": {
        cause: "unicode character",
        title: "Invalid character in identifier",
    },
    "invalid_keyword_argument": {
        cause: "where `invalid` is not a valid ",
        title: "Keyword can't be an expression",
    },
    "keyword_as_attribute": {
        cause: "keyword `pass` as an attribute",
        title: "Keyword as attribute",
    },
    "lambda_with_parens": {
        cause: "`lambda` does not allow parentheses ",
        title: "lambda with parentheses around arguments"
    },
    "lambda_with_tuple_argument": {
        cause: "You cannot have explicit tuples as arguments.",
        title: "lambda with tuple as argument"
    },
    "missing_colon_if": {
        cause: "`if` but forgot to add a colon `:`",
        title: "Missing colon - if",
    },
    "missing_colon_while": {
        cause: "wrote a `while` loop but",
        title: "Missing colon - while",
    },
    "missing_comma_in_dict": {
        cause: "forgot a comma",
        title: "Missing comma in a dict",
    },
    "missing_comma_in_list": {
        cause: "The following lines of code",
        title: "Missing comma in a list",
    },
    "missing_comma_in_set": {
        cause: "The following lines of code",
        title: "Missing comma in a set",
    },
    "missing_comma_in_tuple": {
        cause: "The following lines of code",
        title: "Missing comma in a tuple",
    },
    "print_is_a_function": {
        cause: "In older version of Python, `print` was a keyword",
        title: "print is a function",
    },
    "quote_inside_string": {
        cause: "quote inside a string",
        title: "Quote inside a string",
    },
    "unclosed_bracket": {
        cause: "The opening square bracket `[`",
        title: "Unclosed bracket",
    },
    "unclosed_paren_1": {
        cause: "The opening parenthesis `(` on line",
        title: "Unclosed parenthesis - 1",
    },
    "unclosed_paren_2": {
        cause: "The opening parenthesis `(` on line",
        title: "Unclosed parenthesis - 2",
    },
    "unexpected_after_continuation_character": {
        cause: "using the continuation character",
        title: "Content passed continuation line character",
    },
    "unexpected_eof": {
        cause: "The opening square bracket `[`",
        title: "Unexpected EOF while parsing",
    },
    "unmatched_closing_paren": {
        cause: "The closing parenthesis `)` on",
        title: "Unmatched closing parenthesis",
    },
    "unmatched_closing_bracket_1": {
        cause: "The closing square bracket `]` on line",
        title: "Mismatched brackets - 1",
    },
    "unmatched_closing_bracket_2": {
        cause: "The closing square bracket `]` on line",
        title: "Mismatched brackets - 2",
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
    "raise_syntax_error107": {
        cause: "You started writing a triple-quoted string",
        title: "Unterminated triple quoted string",
    },
    "raise_syntax_error108": {
        cause: "and rename it using the Python keyword `as`",
        title: "Incorrect use of 'from module import ... as ...",
    },
    "raise_syntax_error109": {
        cause: "The correct order depends if there is an `else` clause or not",
        title: "Comprehension with condition (no else)",
    },
    "raise_syntax_error110": {
        cause: "The correct order depends if there is an `else` clause or not",
        title: "Comprehension with condition (with else)",
    },
    "raise_syntax_error111": {
        cause: "Did you mean `0o1`",
        title: "Forgot 'o' for octal",
    },
    "raise_syntax_error112": {
        cause: "Did you mean `123_456`",
        title: "Integer with leading zeros",
    },
    "raise_syntax_error113": {
        cause: "and forgot to include parentheses around tuples",
        title: "Missing () for tuples in comprehension",
    },
    "raise_syntax_error114": {
        cause: "`bf` is an illegal string prefix.",
        title: "Binary f-string not allowed",
    },
    "raise_syntax_error115": {
        cause: "with multiple exception types.",
        title: "Parens around multiple exceptions",
    },
    "raise_syntax_error116": {
        cause: "You used a number as an argument",
        title: "Single number used as arg in function def",
    },
    "raise_syntax_error117": {
        cause: "You used numbers as arguments",
        title: "Numbers used as arg in function def",
    },
    "raise_syntax_error118": {
        cause: "I suspect that you used a number as an argument",
        title: "Number and string used as arg in function def",
        "other causes": ["there might be other syntax errors"],
    },
    "raise_syntax_error119": {
        cause: "You used a string as an argument",
        title: "Single string used as arg in function def",
    },
    "raise_syntax_error120": {
        cause: "You used strings as arguments",
        title: "Strings used as arg in function def",
    },
    "raise_syntax_error121": {
        cause: "I suspect that you used a string as an argument",
        title: "String and number used as arg in function def",
        "other causes": ["there might be other syntax errors"],
    },
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
    descriptions["quote_inside_string"]["cause"] = "ended the string with another quote"
    del descriptions["missing_comma_in_set"]  # Temporary due to a bug in CPython
    del descriptions["missing_comma_in_list"]  # Temporary due to a bug in CPython
    del descriptions["unclosed_bracket"]  # Temporary due to a bug in CPython
