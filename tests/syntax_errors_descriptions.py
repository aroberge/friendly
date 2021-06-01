"""In this file, descriptions is a dict whose keys are the names of
Python files that raise a SyntaxError (or subclass) when they are imported.

"in cause" is some text that should be found in the explanation provided by
        Friendly-traceback when importing this file.

"title" is the heading that should appear in the documentation for
        this particular case.

"also in cause" is a list of text fragments that should also be found in the explanation

"not in cause" is a list of text fragments that should not be found in the explanation.
"""
import sys

cause = "in cause"
title = "title"

descriptions = {
    "and_in_import_statement": {
        cause: "only be used for boolean expressions",
        title: "Using 'and' in import statement",
    },
    "annotated_name_global": {
        cause: "It cannot be declared to be a global variable.",
        title: "Annotated name cannot be global",
    },
    "as_instead_of_comma_in_import": {
        cause: "and rename it using the Python keyword `as`",
        title: "Incorrect use of 'from module import ... as ...",
    },
    "assign_name_before_global_1": {
        cause: "before declaring it as a global variable.",
        title: "Name assigned prior to global declaration",
    },
    "assign_name_before_global_2": {
        cause: "You used the variable `r`",
        title: "Name used prior to global declaration",
    },
    "assign_name_before_nonlocal_1": {
        cause: "before declaring it as a nonlocal variable.",
        title: "Name used prior to nonlocal declaration",
    },
    "assign_name_before_nonlocal_2": {
        cause: "You assigned a value to the variable `s`",
        title: "Name assigned prior to nonlocal declaration",
    },
    "assign_to_conditional": {
        cause: "variable = object if condition else other_object",
        title: "Assign to conditional expression",
    },
    "assign_to_debug": {
        cause: "`__debug__` is a constant in Python",
        title: "Assignment to keyword (__debug__)",
    },
    "assign_to_debug2": {
        cause: "`__debug__` is a constant in Python",
        title: "Assignment to keyword (__debug__)",
    },
    "assign_to_ellipsis": {
        cause: "The ellipsis symbol `...` is a constant in Python",
        title: "Assignment to Ellipsis symbol",
    },
    "assign_to_f_string": {
        cause: "expression that has the f-string",
        title: "Cannot assign to f-string",
    },
    "assign_to_function_call_1": {
        cause: "function call and is not simply the name of a variable",
        title: "Cannot assign to function call: single = sign",
        "also in cause": ["len('a')"],
    },
    "assign_to_function_call_2": {
        cause: "function call and not the name of a variable",
        title: "Cannot assign to function call: two = signs",
        "also in cause": ["func(...)"],
    },
    "assign_to_generator": {
        cause: "generator expression instead of the name of a variable",
        title: "Assign to generator expression",
    },
    "assign_to_literal_dict": {
        cause: "is or includes an actual object of type `dict`",
        title: "Cannot assign to literal - 4",
    },
    "assign_to_literal_int": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal int",
        "also in cause": ["Perhaps you meant to write"],
    },
    "assign_to_literal_int_2": {
        cause: "is or includes an actual object of type `int`",
        title: "Cannot assign to literal int - 2",
    },
    "assign_to_literal_int_3": {
        cause: "is or includes an actual object",
        title: "Cannot assign to literal - 5",
    },
    "assign_to_literal_set": {
        cause: "is or includes an actual object of type `set`",
        title: "Cannot assign to literal - 3",
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
    "assign_to_operation": {
        cause: "only used to assign a value to a variable",
        title: "Assign to math operation",
    },
    "augmented_assignment_to_literal": {  # May differ depending on Python version
        cause: "the walrus operator, with literals like",
        title: "Augmented assignment to literal"
    },
    "augmented_assigment_with_true": {  # May differ depending on Python version
        cause: "`True` is a constant in Python",
        title: "Walrus/Named assignment depending on Python version",
    },
    "backslash_instead_of_slash": {
        cause: "Did you mean to divide",
        title: "Backslash instead of slash",
    },
    "break_outside_loop": {
        cause: "The Python keyword `break` can only be used",
        title: "break outside loop",
    },
    "cannot_use_star": {
        cause: "The star operator",
        title: "Cannot use star operator",
    },
    "cannot_use_double_star": {
        cause: "The double star operator",
        title: "Cannot use double star operator",
    },
    "class_missing_name" : {
        cause: "A class needs a name.",
        title: "Missing class name"
    },
    "comprehension_missing_tuple_paren": {
        cause: "and forgot to include parentheses around tuples",
        title: "Missing () for tuples in comprehension",
    },
    "comprehension_with_condition_no_else": {
        cause: "The correct order depends if there is an `else` clause or not",
        title: "Comprehension with condition (no else)",
    },
    "comprehension_with_condition_with_else": {
        cause: "The correct order depends if there is an `else` clause or not",
        title: "Comprehension with condition (with else)",
    },
    "continue_outside_loop": {
        cause: "The Python keyword `continue` can only be used",
        title: "continue outside loop",
    },
    "copy_pasted_code": {
        cause: "copy-pasted code from an interactive interpreter",
        title: "Copy/paste from interpreter",
    },
    "def_arg_after_kwarg": {
        cause: "Positional arguments must come before keyword argument",
        title: "def: positional arg after kwargs",
    },
    "def_bare_star_arg": {
        cause: "replace `*` by either `*arguments` or ",
        title: "def: named arguments must follow bare *",
    },
    "def_code_block": {
        cause: "tried to define a function",
        title: "def: misused as code block",
    },
    "def_dict_as_arg": {
        cause: "You cannot have any explicit dict or set as function arguments",
        title: "def: dict as argument",
    },
    "def_duplicate_arg": {
        cause: "keyword argument should appear only once in a function definition",
        title: "def: Keyword arg only once in function definition",
    },
    "def_extra_semi_colon": {
        cause: "Did you write something by mistake after the colon",
        title: "def: semi-colon after colon",
    },
    "def_extra_comma": {
        cause: "Did you mean to write `,`",
        title: "def: extra comma"
    },
    "def_forward_slash_1": {
        cause: "You have unspecified keyword arguments that appear before",
        title: "def: unspecified keywords before /",
    },
    "def_forward_slash_2": {
        cause: "When they are used together, `/` must appear before `*`",
        title: "def: / before star",
    },
    "def_forward_slash_3": {
        cause: "`*arg` must appear after `/` in a function definition",
        title: "def: / before star arg",
    },
    "def_forward_slash_4": {
        cause: "You can only use `/` once in a function definition",
        title: "def: / used twice",
    },
    "def_function_name_invalid": {
        cause: "The name of a function must be a valid Python identifier",
        title: "def: non-identifier as a function name",
    },
    "def_function_name_string": {
        cause: "use a string as a function name",
        title: "def: using a string as a function name",
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
    "def_list_as_arg_1": {
        cause: "You cannot have explicit lists as function arguments",
        title: "def: list as argument - 1",
    },
    "def_list_as_arg_2": {
        cause: "You cannot have explicit lists as function arguments",
        title: "def: list as argument - 2",
    },
    "def_missing_colon": {
        cause: "Did you forget to write a colon",
        title: "def: missing colon",
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
    "def_number_as_arg": {
        cause: "You used a number as an argument",
        title: "Single number used as arg in function def",
    },
    "def_operator_instead_of_comma": {
        cause: "Did you mean to write a comma",
        title: "def: operator instead of comma"
    },
    "def_operator_instead_of_equal": {
        cause: "Did you mean to write an equal sign",
        title: "def: operator instead of equal"
    },
    "def_operator_instead_of_name": {
        cause: "If you replace it by a unique variable name",
        title: "def: operator instead of name"
    },
    "def_positional_after_keyword_arg": {
        cause: "call functions with only positional arguments",
        title: "def: positional argument follows keyword argument",
    },
    "def_semi_colon_instead_of_colon": {
        cause: "You wrote `;` instead of a colon",
        title: "def: semi-colon instead of colon",
    },
    "def_set_as_arg": {
        cause: "You cannot have any explicit dict or set as function arguments",
        title: "def: set as argument",
    },
    "def_star_arg_before_slash": {
        cause: "`*arg` must appear after `/` ",
        title: "def: ``*arg`` before /",
    },
    "def_star_used_only_once": {
        cause: "can only use `*` once in a function definition",
        title: "def: ``*`` used twice",
    },
    "def_string_as_arg": {
        cause: "You used a string as an argument",
        title: "Single string used as arg in function def",
    },
    "def_tuple_as_arg_1": {
        cause: "You cannot have explicit tuples as function arguments.",
        title: "def: tuple as function argument",
    },
    "def_tuple_as_arg_2": {
        cause: "You cannot have explicit tuples as function arguments.",
        title: "def: tuple as function argument - 2",
    },
    "delete_constant_keyword": {
        cause: "You cannot delete the constant",
        title: "Deleting constant/keyword",
    },
    "delete_function_call": {
        cause: "instead of deleting the function's name",
        title: "Cannot delete function call",
    },
    "delete_string_literal": {
        cause: "You cannot delete the literal",
        title: "Deleting string literal",
    },
    "different_operators_in_a_row": {
        cause: "You cannot have these two operators, `*` and `/`",
        title: "Different operators in a row"
    },
    "dot_before_paren": {
        cause: "dot `.` followed by `(`",
        title: "Dot followed by parenthesis",
    },
    "duplicate_token": {
        cause: "wrote [`,`] twice in a row by mistake",
        title: "Extra token"
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
    "except_multiple_exceptions": {
        cause: "with multiple exception types.",
        title: "Parens around multiple exceptions",
    },
    "extra_token" : {
      cause: "wrote `==` by mistake",
      title: "Extra token"
    },
    "f_string_binary": {
        cause: "`bf` is an illegal string prefix.",
        title: "Binary f-string not allowed",
    },
    "f_string_unterminated": {
        cause: "you have another string, which starts with either",
        title: "f-string: unterminated string",
    },
    "f_string_with_backslash": {
        cause: "you can replace the part that contains a backslash",
        title: "f-string with backslash",
    },
    "for_missing_terms": {
        cause: "A `for` loop is an iteration over a sequence",
        title: "Missing terms in for statement"
    },
    "future_braces": {
        cause: "from __future__ import braces",
        title: "Not a chance!",
    },
    "future_import_star": {
        cause: "you must import specific named features",
        title: "Do not import * from __future__",
    },
    "future_must_be_first": {
        cause: "It must appear at the beginning of the file.",
        title: "__future__ at beginning",
    },
    "future_typo": {
        cause: "Did you mean `division`",
        title: "Typo in __future__",
    },
    "future_unknown": {
        cause: "print_function",
        title: "Unknown feature in __future__",
    },
    "generator_expression_parens": {
        cause: "must add parentheses enclosing",
        title: "Parenthesis around generator expression",
    },
    "hyphen_instead_of_underscore": {
        cause: "Did you mean `a_b`",
        title: "Space between names",
    },
    "if_missing_condition": {
        cause: "An `if` statement requires a condition",
        title: "Missing condition in if statement"
    },
    "imaginary_i": {
        cause: "Did you mean `3.0j`",
        title: "use j instead of i",
    },
    "import_from": {
        cause: "from turtle import pen",
        title: "Import inversion: import X from Y",
    },
    "indentation_error_1": {
        cause: "expected to begin a new indented block",
        title: "IndentationError: expected an indented block",
    },
    "indentation_error_2": {
        cause: "is more indented than expected",
        title: "IndentationError: unexpected indent",
    },
    "indentation_error_3": {
        cause: "is less indented than expected",
        title: "IndentationError: unindent does not match ...",
    },
    "indentation_error_4": {
        cause: "meant to include a continuation character",
        title: "IndentationError: missing continuation line",
    },
    "integer_with_leading_zero_1": {
        cause: "Did you mean `0o1`",
        title: "Forgot 'o' for octal",
    },
    "integer_with_leading_zero_2": {
        cause: "Did you mean `123_456`",
        title: "Integer with leading zeros",
    },
    "invalid_character_in_identifier": {
        cause: "unicode character",
        title: "Invalid character in identifier",
    },
    "invalid_hexadecimal": {
        cause: "Did you made a mistake in writing an hexadecimal integer",
        title: "Invalid hexadecimal number",
    },
    "invalid_identifier": {
        cause: "Valid names cannot begin with a number",
        title: "Valid names cannot begin with a number",
        "not in cause": ["complex"],
    },
    "invalid_identifier_2": {
        cause: "Perhaps you forgot a multiplication operator",
        title: "Valid names cannot begin with a number - 2",
        "not in cause": ["complex"],
    },
    "invalid_identifier_3": {
        cause: "Perhaps you forgot a multiplication operator",
        title: "Valid names cannot begin with a number - 3",
        "also in cause": ["complex"],
    },
    "invalid_identifier_4": {
        cause: "Valid names cannot begin with a number",
        title: "Valid names cannot begin with a number - 4",
        "not in cause": ["multiplication operator"],
    },
    "invalid_identifier_5": {
        cause: "Valid names cannot begin with a number",
        title: "Valid names cannot begin with a number - 5",
        "also in cause": ["complex", "multiplication operator"],
    },
    "invalid_keyword_argument": {
        cause: "where `invalid` is not a valid ",
        title: "Keyword can't be an expression",
    },
    "invalid_octal": {
        cause: "Did you made a mistake in writing an octal integer",
        title: "Invalid octal number",
    },
    "inverted_operators" :{
        cause: "Did you write operators in an incorrect order?",
        title: "Inverted operators 1"
    },
    "inverted_operators_2": {
        cause: "Did you write operators in an incorrect order?",
        title: "Inverted operators 2",
        "also in cause": ["all the syntax errors in the code you wrote"]
    },
    "keyword_arg_repeated": {
        cause: "keyword argument should appear only once in a function call",
        title: "Keyword arg only once in function call",
    },
    "keyword_as_attribute": {
        cause: "keyword `pass` as an attribute",
        title: "Keyword as attribute",
    },
    "lambda_with_parens": {
        cause: "`lambda` does not allow parentheses ",
        title: "lambda with parentheses around arguments",
    },
    "lambda_with_tuple_argument": {
        cause: "You cannot have explicit tuples as arguments.",
        title: "lambda with tuple as argument",
    },
    "literal_in_for_loop": {
        cause: "where `...` must contain only identifiers",
        title: "Assign to literal in for loop"
    },
    "missing_code_block": {  # May differ depending on Python version
        cause: "it reached the end of the file and expected more content.",
        title: "IndentationError/SyntaxError depending on version",
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
    "missing_parens_for_range": {
        cause: "you forgot to use to use parenthesis with `range`",
        title: "Missing parenthesis for range"
    },
    "name_is_global_and_nonlocal": {
        cause: "You declared `xy` as being both a global and nonlocal",
        title: "Name is global and nonlocal",
    },
    "name_is_param_and_nonlocal": {
        cause: "You used `x` as a parameter for a function",
        title: "Name is parameter and nonlocal",
    },
    "no_binding_for_nonlocal": {
        cause: "nonlocal variable but it cannot be found.",
        title: "nonlocal variable not found",
    },
    "nonlocal_at_module": {
        cause: "You used the nonlocal keyword at a module level",
        title: "nonlocal variable not found at module level",
    },
    "operator_twice_in_a_row": {
        cause: "You cannot have write the same operator, `**`, twice in a row",
        title: "Same operator twice in a row",
    },
    "pip_install_1": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "Using pip from interpreter",
    },
    "pip_install_2": {
        cause: "`pip` is a command that needs to run in a terminal",
        title: "Using pip from interpreter 2",
    },
    "print_is_a_function": {
        cause: "In older version of Python, `print` was a keyword",
        title: "print is a function",
    },
    "print_is_a_function_2": {
        cause: "In older version of Python, `print` was a keyword",
        title: "print is a function 2",
    },
    "quote_inside_string": {
        cause: "quote inside a string",
        title: "Quote inside a string",
    },
    "raise_multiple_exceptions": {
        cause: "trying to raise an exception using Python 2 syntax.",
        title: "Raising multiple exceptions",
    },
    "return_outside_function": {
        cause: "You can only use a `return`",
        title: "Cannot use return outside function",
    },
    "single_equal_with_if": {
        cause: "You likely used an assignment operator `=`",
        title: "Single = instead of double == with if",
    },
    "single_equal_with_elif": {
        cause: "You likely used an assignment operator `=`",
        title: "Single = instead of double == with elif",
    },
    "single_equal_with_while": {
        cause: " used an assignment operator `=`",
        title: "Single = instead of double == with while",
    },
    "space_between_operators_1": {
        cause : "meant to write `**` as a single operator",
        title: "Space between operators 1"
    },
    "space_between_operators_2": {
        cause: "meant to write `/=` as a single operator",
        title: "Space between operators 2"
    },
    "too_many_nested_blocks": {
        cause: "Seriously",
        title: "Too many nested blocks",
    },
    "triple_equal": {
        cause: "the exact same object, use the operator `is`",
        title: "Triple-equal sign",
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
    "unclosed_paren_3": {
        cause: "The opening parenthesis `(` on line 5 is not closed",
        title: "Unclosed parenthesis - 3",
    },
    "unexpected_after_continuation_character": {
        cause: "using the continuation character",
        title: "Content passed continuation line character",
    },
    "unexpected_eof": {
        cause: "The opening square bracket `[`",
        title: "Unexpected EOF while parsing",
    },
    "unicode_quote": {
        cause: "fancy unicode quotation mark",
        title: "Invalid character (unicode quote)",
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
    "unterminated_triple_quote_string": {
        cause: "You started writing a triple-quoted string",
        title: "Unterminated triple quoted string",
    },
    "tab_error": {
        cause: "A `TabError` indicates that you have used",
        title: "TabError",
    },
    "unescaped_backslash": {
        cause: "Did you forget to escape a backslash character",
        title: "EOL unescaped backslash",
    },
    "use_backquote": {
        cause: "use the function `repr(x)`.",
        title: "Using the backquote character",
    },
    "while_missing_condition": {
        cause: "A `while` loop requires a condition",
        title: "Missing condition in while statement"
    },
    "would_be_type_declaration_1": {
        cause: "You do not need to declare variables in Python.",
        title: "Would-be variable declaration",
    },
    "would_be_type_declaration_2": {
        cause: "You do not need to declare variables in Python.",
        title: "Would-be variable declaration - 2",
    },
}

if sys.version_info < (3, 8):
    descriptions["augmented_assigment_with_true"]["in cause"] = "walrus operator"
    descriptions["augmented_assignment_to_literal"]["in cause"] = "walrus operator"
    descriptions["walrus_does_not_exist"] = {
        cause: "walrus operator",
        title: "Walrus operator does not exist - yet",
    }
    no_slash = (
        "Function definitions cannot include the symbol `/` in this Python version"
    )
    descriptions["def_forward_slash_1"]["in cause"] = no_slash
    descriptions["def_forward_slash_2"]["in cause"] = no_slash
    descriptions["def_forward_slash_3"]["in cause"] = no_slash
    descriptions["def_forward_slash_4"]["in cause"] = no_slash

    del descriptions["would_be_type_declaration_1"]
    del descriptions["would_be_type_declaration_2"]
    descriptions["def_star_arg_before_slash"][
        "in cause"
    ] = "This symbol can only be used with Python versions"

if sys.version_info >= (3, 9):
    descriptions["missing_code_block"]["in cause"] = "expected an indented block"

if sys.version_info >= (3, 10):
    descriptions["quote_inside_string"]["in cause"] = "ended the string with another quote"
    descriptions["missing_colon_if"]["in cause"] = "Did you forget a colon"
    descriptions["missing_colon_while"]["in cause"] = "Did you forget a colon"
    descriptions["def_missing_colon"][
        "in cause"
    ] = "but forgot to add a colon `:` at the end"

    # Temporary removal while taking into account changes in Python 3.10
    del descriptions["equal_sign_instead_of_colon"]
    del descriptions["invalid_hexadecimal"]
    del descriptions["missing_comma_in_list"]
    del descriptions["missing_comma_in_set"]
    del descriptions["missing_comma_in_tuple"]
    del descriptions["print_is_a_function_2"]
    del descriptions["single_equal_with_if"]
    del descriptions["single_equal_with_elif"]
    del descriptions["single_equal_with_while"]
    del descriptions["would_be_type_declaration_1"]
    del descriptions["would_be_type_declaration_2"]
