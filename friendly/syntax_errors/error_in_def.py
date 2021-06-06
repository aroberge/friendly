"""In this module, we try to identify a remedy to a syntax error
associated with a 'def' statement.
"""
import platform
import sys

from . import fixers
from ..my_gettext import current_lang, internal_error
from .. import debug_helper
from .. import utils

STATEMENT_ANALYZERS = []

ASYNC = 0


def more_errors():
    _ = current_lang.translate
    return "\n" + _(
        "However, making such a change would still not correct\n"
        "all the syntax errors in the code you wrote.\n"
    )


def def_correct_syntax():
    _ = current_lang.translate
    async_ = "" if ASYNC == 0 else "async "
    # fmt: off
    return _(
        "The correct syntax is:\n\n"
        "    {async_}def name ( ... ):"
    ).format(async_=async_) + "\n"
    # fmt: on


def add_statement_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single statement."""
    STATEMENT_ANALYZERS.append(func)


# ========================================================
# Main calling function
# ========================================================


def analyze_def_statement(statement):
    """Analyzes the statement as identified by Python as that
    on which the error occurred."""
    global ASYNC
    if not statement.tokens:  # pragma: no cover
        debug_helper.log("Statement with no tokens in error_in_def.py")
        return {"cause": internal_error()}

    ASYNC = 0
    if statement.tokens[0] == "async":
        ASYNC = 1

    if len(statement.tokens) > 1 + ASYNC and str(statement.tokens[1 + ASYNC]) in (
        "=",
        ":=",
    ):
        # Let the generic method handle the wrong assignment case
        return {}

    for analyzer in STATEMENT_ANALYZERS:
        cause = analyzer(statement)
        if cause:
            return cause
    return {}


@add_statement_analyzer
def def_begin_code_block(statement):  #
    # Thinking of trying to use def to begin a code block, i.e.
    # def : ...
    _ = current_lang.translate
    if statement.nb_tokens > 2 + ASYNC or statement.bad_token != ":":
        return {}

    if statement.first_token.start_col == 0:
        hint = _("A function needs a name.\n")
        cause = _(
            "You tried to define a function and did not use the correct syntax.\n"
        )
    else:
        hint = _("Functions and methods need a name.\n")
        cause = _(
            "You tried to define a function or method and did not use the correct syntax.\n"
        )

    return {"cause": cause + def_correct_syntax(), "suggest": hint}


@add_statement_analyzer
def missing_parens(statement):
    # Something like
    # def test: ...
    _ = current_lang.translate

    if (
        statement.bad_token != ":"
        and statement.nb_tokens >= 3 + ASYNC
        and statement.bad_token != statement.tokens[2 + ASYNC]
    ):
        return {}

    new_statement = fixers.modify_token(
        statement.statement_tokens, statement.bad_token, prepend="()"
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget parentheses?\n")
        cause = _(
            "Perhaps you forgot to include parentheses.\n"
            "You might have meant to write\n\n"
            "    {line}\n"
        ).format(line=new_statement)
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def missing_parens_2(statement):
    # Something like
    # def test a, b:
    _ = current_lang.translate

    if statement.bad_token_index != 2 + ASYNC and statement.last_token != ":":
        return {}

    new_statement = fixers.replace_two_tokens(
        statement.statement_tokens,
        statement.bad_token,
        first_string="(" + statement.bad_token.string,
        second_token=statement.last_token,
        second_string="):",
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget parentheses?\n")
        cause = _(
            "Perhaps you forgot to include parentheses.\n"
            "You might have meant to write\n\n"
            "    {line}\n"
        ).format(line=new_statement)
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def missing_colon(statement):
    """look for missing colon at the end of statement; includes the case where
    something else has been written as a typo."""
    _ = current_lang.translate
    if (
        statement.last_token == ":"
        or statement.bad_token != statement.last_token
        or statement.statement_brackets
    ):
        return {}
    cause = _("A function definition statement must end with a colon.\n")

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, ":"
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget to write a colon?\n")
        cause += _("You wrote `{bad}` instead of a colon.\n").format(
            bad=statement.bad_token
        )
        return {"cause": cause, "suggest": hint}

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, ""
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you write something by mistake after the colon?\n")
        cause += _("A block of code must come after the colon.\n")
        cause += _("Removing `{bad}`, might fix the problem.\n").format(
            bad=statement.bad_token
        )
        return {"cause": cause, "suggest": hint}

    new_statement = fixers.modify_token(
        statement.statement_tokens, statement.bad_token, append=":"
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you forget to write a colon?\n")
        return {"cause": cause, "suggest": hint}

    return {}


@add_statement_analyzer
def keyword_as_function_name(statement):
    # Something like
    # def pass(): ...
    _ = current_lang.translate
    def_token = statement.tokens[ASYNC]
    if not (statement.bad_token.is_keyword() and statement.prev_token == def_token):
        return {}

    hint = _("You cannot use a Python keyword as a function name.\n")
    cause = _(
        "You tried to use the Python keyword `{kwd}` as a function name.\n"
    ).format(kwd=statement.bad_token)

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, "name"
    )
    if not fixers.check_statement(new_statement):
        cause += "\n" + _("There are more syntax errors later in your code.\n")

    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def other_invalid_function_names(statement):
    _ = current_lang.translate
    def_token = statement.tokens[ASYNC]
    if statement.bad_token.is_identifier() or not (statement.prev_token == def_token):
        return {}

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, "name"
    )
    if not fixers.check_statement(new_statement):
        return {}

    hint = _("You wrote an invalid function name.\n")
    cause = _(
        "The name of a function must be a valid Python identifier,\n"
        "that is a name that begins with a letter or an underscore character, `_`,\n"
        "and which contains only letters, digits or the underscore character.\n"
    )
    if statement.bad_token.is_string():
        cause += _("You attempted to use a string as a function name.\n")
        hint = cause
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def function_definition_missing_name(statement):
    _ = current_lang.translate
    def_token = statement.tokens[ASYNC]
    if not (
        def_token == "def"
        and statement.bad_token == "("
        and statement.prev_token == def_token
    ):
        return {}

    cause = _("You forgot to name your function.\n")

    new_statement = fixers.replace_token(
        statement.tokens, statement.bad_token, "name ("
    )
    if fixers.check_statement(new_statement):
        return {"cause": cause + def_correct_syntax()}

    cause += _("However, there are some other syntax errors in your code.\n")
    return {"cause": cause + def_correct_syntax()}


@add_statement_analyzer
def keyword_not_allowed_as_function_argument(statement):
    _ = current_lang.translate
    if not (statement.bad_token.is_keyword() and statement.begin_brackets):
        return {}

    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, "name"
    )
    if not fixers.check_statement(new_statement):
        return {}

    cause = _(
        "I am guessing that you tried to use the Python keyword\n"
        "`{kwd}` as an argument in the definition of a function\n"
        "where an identifier (variable name) was expected.\n"
    ).format(kwd=statement.bad_token)

    return {"cause": cause}


@add_statement_analyzer
def dotted_name_not_allowed(statement):
    _ = current_lang.translate
    if not (statement.bad_token == "." and statement.prev_token.is_identifier()):
        return {}

    if statement.bad_token_index > 3 + ASYNC:
        cause = _("You cannot use dotted names as function arguments.\n")
        if statement.next_token.is_identifier():
            cause += _("Perhaps you meant to write a comma.\n")
            hint = _("Did you mean to write a comma?\n")
        else:
            hint = cause
    else:
        hint = cause = _("You cannot use dots in function names.\n")
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def positional_arguments_in_def(statement):
    _ = current_lang.translate

    if statement.bad_token != "/" or statement.prev_token.string not in "(,":
        return {}

    meaning = _(
        "`/` indicates that the previous arguments in a function definition\n"
        "are positional arguments.\n"
    )

    if sys.version_info < (3, 8):
        hint = _(
            "Function definitions cannot include the symbol `/` in this Python version.\n"
        )
        cause = meaning + _(
            "This symbol can only be used with Python versions 3.8.0 or newer.\n"
            "You are using Python version {version}.\n"
        ).format(version=platform.python_version())
        return {"cause": cause, "suggest": hint}

    prev_tok = ""
    for tok in statement.tokens[ASYNC : statement.bad_token_index]:
        if tok == "**":
            cause = meaning + _(
                "You have unspecified keyword arguments that appear before\n"
                "the symbol `/`.\n"
            )
            hint = _("Keyword arguments must appear after the `/` symbol.\n")  # yes
            return {"cause": cause, "suggest": hint}

        if prev_tok == "*":  # might be incorrect if used in *args
            if tok == ",":
                cause = meaning + _(
                    "However, `*` indicates that the arguments\n"
                    "that follow must be keyword arguments.\n"
                    "When they are used together, `/` must appear before `*`.\n"
                )
                hint = _("`*` must appear after `/` in a function definition.\n")
            else:
                hint = _(
                    "`*{name}` must appear after `/` in a function definition.\n"
                ).format(name=tok.string)
                cause = meaning + hint
            return {"cause": cause, "suggest": hint}

        if tok == "/" and prev_tok == ",":
            cause = _("You can only use `/` once in a function definition.\n")
            return {"cause": cause, "suggest": cause}

        prev_tok = tok

    return {}


@add_statement_analyzer
def keyword_arguments_in_def(statement):
    _ = current_lang.translate
    if statement.bad_token != "*" or statement.prev_token != ",":
        return {}

    args = statement.next_token if statement.next_token.is_identifier() else ""
    hint = _("You can only use `*` once in a function definition.\n")
    tokens = statement.tokens
    for index, tok in enumerate(tokens[ASYNC : statement.bad_token_index]):
        next_token = tokens[index + 1]
        if tok == "*":
            if next_token.is_identifier() and args:
                cause = hint + _(
                    "You have used it twice, with `*{first}` and `*{second}`.\n"
                ).format(first=next_token, second=args)
                return {"cause": cause, "suggest": hint}
            elif next_token.is_identifier():
                args = next_token.string

            if args:
                cause = hint + _(
                    "It must either be used by itself, `*`,\n"
                    "or in the form `*{args}`, but not both.\n"
                ).format(args=args)
            else:
                cause = hint
            return {"cause": cause, "suggest": hint}
        elif tok == "**":
            if args:
                cause = _("`*{args}` must appear before `**{kwargs}`.\n").format(
                    args=args, kwargs=next_token
                )
            else:
                cause = _("`**{kwargs}` must appear after the `*` operator.\n").format(
                    kwargs=next_token
                )
            return {"cause": cause, "suggest": hint}
    else:  # pragma: no cover
        debug_helper.log("New case to consider for * as bad token.")
        return {"cause": hint, "suggest": hint}


@add_statement_analyzer
def number_as_argument(statement):
    _ = current_lang.translate

    if not (statement.bad_token.is_number() and statement.prev_token.string in "(,"):
        return {}

    hint = _("You cannot use numbers as function arguments.\n")
    cause = _(
        "You used a number as an argument when defining a function.\n"
        "You can only use identifiers (variable names) as function arguments.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def string_as_argument(statement):
    _ = current_lang.translate

    if not (statement.bad_token.is_string() and statement.prev_token.string in "(,"):
        return {}

    hint = _("You cannot use strings as function arguments.\n")
    cause = _(
        "You used a string as an argument when defining a function.\n"
        "You can only use identifiers (variable names) as function arguments.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def tuple_as_argument(statement):
    _ = current_lang.translate

    if statement.bad_token != "(" or statement.prev_token.string not in "(,":
        return {}

    hint = _("You cannot have explicit tuples as function arguments.\n")

    cause = hint + _(
        "You can only use identifiers (variable names) as function arguments.\n"
        "Assign any tuple to a parameter and unpack it\n"
        "within the body of the function.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def list_as_argument(statement):
    _ = current_lang.translate
    if statement.bad_token != "[" or statement.prev_token.string not in "(,":
        return {}

    hint = _("You cannot have explicit lists as function arguments.\n")
    cause = hint + _(
        "You can only use identifiers (variable names) as function arguments.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def dict_or_set_as_argument(statement):
    _ = current_lang.translate
    if statement.bad_token != "{" or statement.prev_token.string not in "(,":
        return {}

    hint = _("You cannot have any explicit dict or set as function arguments.\n")
    cause = hint + _(
        "You can only use identifiers (variable names) as function arguments.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def operator_as_argument(statement):
    """This looks at various possible fixes when the bad token is an operator.
    The following cases are considered:
    1. operator instead of comma
    1. operator instead of equal sign
    """
    _ = current_lang.translate
    if not statement.bad_token.is_operator() or statement.prev_token == "def":
        return {}

    no_op = _("You cannot have operators as function arguments.\n")

    # def test(a+b): -> def test(a, b):
    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, ","
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you mean to write a comma?\n")
        cause = no_op + _(
            "I suspect you made a typo and wrote `{op}` instead of a comma.\n"
            "The following statement contains no syntax error:\n\n"
            "    {new_statement}"
        ).format(op=statement.bad_token, new_statement=new_statement)
        return {"cause": cause, "suggest": hint}

    # def test(a=1, b+2):  -> def test(a=1, b=2):
    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, "="
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you mean to write an equal sign?\n")
        cause = no_op + _(
            "I suspect you made a typo and wrote `{op}` instead of an equal sign.\n"
            "The following statement contains no syntax error:\n\n"
            "    {new_statement}"
        ).format(op=statement.bad_token, new_statement=new_statement)
        return {"cause": cause, "suggest": hint}

    # def test(a,,b):  -> def test(a,b):
    new_statement = fixers.replace_token(
        statement.statement_tokens, statement.bad_token, ""
    )
    if fixers.check_statement(new_statement):
        hint = _("Did you mean to write `{op}`?\n").format(op=statement.bad_token)
        cause = _(
            "I suspect you made a typo and added `{op}` by mistake.\n"
            "The following statement contains no syntax error:\n\n"
            "    {new_statement}"
        ).format(op=statement.bad_token, new_statement=new_statement)
        if statement.bad_token != ",":
            cause = no_op + cause
        return {"cause": cause, "suggest": hint}

    # def test(a, **, b): -> def test(a, c, b):
    if statement.prev_token.string in ("(", ","):
        # prevent getting an error because of repeated argument
        unique_name = utils.unique_variable_name()
        new_statement = fixers.replace_token(
            statement.statement_tokens, statement.bad_token, unique_name
        )
        hint = _("You cannot use `{op}` as an argument.\n").format(
            op=statement.bad_token
        )
        if fixers.check_statement(new_statement):
            cause = _(
                "I suspect you made a typo and wrote `{op}` by mistake.\n"
                "If you replace it by a unique variable name, the result\n"
                "will contain no syntax error.\n"
            ).format(op=statement.bad_token)

        else:
            cause = (
                _(
                    "I suspect you made a typo and wrote `{op}` by mistake,\n"
                    "perhaps instead of writing an identifier (variable name).\n"
                )
                + more_errors()
            )
        return {"cause": cause, "suggest": hint}

    if statement.prev_token == "**":
        cause = _(
            "The `**` operator needs to be followed by an identifier (variable name).\n"
        )
        return {"cause": cause}

    return {}  # pragma: no cover


@add_statement_analyzer
def arg_after_kwarg(statement):
    """This is only for something with positional argument after **kwargs;
    the case where we have a positional argument after a named argument,
    (..., a=1, b, ...) gets a specific error message.
    """
    _ = current_lang.translate

    if not (
        statement.bad_token.is_identifier()
        and statement.prev_token == ","
        and statement.next_token in (",", ")")
    ):
        return {}

    for tok in statement.tokens[ASYNC : statement.bad_token_index]:
        if tok == "**":
            hint = _("Positional arguments must come before keyword arguments.\n")
            cause = hint + _(
                "`{arg}` is a positional argument that appears after one or more\n"
                "keyword arguments in your function definition.\n"
            ).format(arg=statement.bad_token.string)
            return {"cause": cause, "suggest": hint}

    return {}
