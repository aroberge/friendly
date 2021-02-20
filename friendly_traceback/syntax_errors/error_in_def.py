"""In this module, we try to identify a remedy to a syntax error
associated with a 'def' statement.
"""

from . import fixers
from ..my_gettext import current_lang, internal_error
from .. import debug_helper
from .. import token_utils

STATEMENT_ANALYZERS = []


def def_correct_syntax():
    _ = current_lang.translate
    # fmt: off
    return _(
        "The correct syntax is:\n\n"
        "    def name ( ... ):"
    ) + "\n"
    # fmt: on


def add_statement_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single statement."""
    STATEMENT_ANALYZERS.append(func)

    def wrapper(statement):
        return func(statement)

    return wrapper


# ========================================================
# Main calling function
# ========================================================


def analyze_def_statement(statement):
    """Analyzes the statement as identified by Python as that
    on which the error occurred."""
    if not statement.tokens:
        debug_helper.log("Statement with no tokens in error_in_def.py")
        return {"cause": internal_error()}

    if statement.tokens[0] == "async":
        statement = remove_async(statement)
        if statement is None:
            return {}

    for analyzer in STATEMENT_ANALYZERS:
        cause = analyzer(statement)
        if cause:
            return cause
    return {}


def remove_async(statement):
    """To simplify the analysis, we replace any statement of the form
    async def ...
    by
    def ...
    """

    if not (statement.tokens[0] == "async" and statement.tokens[1] == "def"):
        debug_helper.log("Problem in remove_async: inconsistent state")
        return None

    statement.tokens.pop(1)
    statement.tokens[0].string = "def"
    statement.bad_token_index -= 1
    statement.nb_tokens -= 1
    statement.prev_token = statement.tokens[statement.bad_token_index - 1]
    try:
        statement.next_token = statement.tokens[statement.bad_token_index + 1]
    except IndexError:
        pass  # undefined statement.next_token should have been already taken care of.

    # We will want to make various text replacement, reconstruct (untokenize) the
    # result to see if it is a valid statement. In doing so, we use the original
    # logical line associated with a given token, and the row/col information.
    # We need to make sure that the line content is consistent with the row/col
    # information.  Thus, we want to replace
    # async    def   something
    # by
    # def            something
    for token in statement.tokens:
        if token.line.strip().startswith("async"):
            token.line = token.line.replace(" def", "", 1)
            token.line = token.line.replace("async", "def      ", 1)
    return statement


@add_statement_analyzer
def missing_parens(statement):
    # Something like
    # def test: ...
    _ = current_lang.translate

    if (
        statement.bad_token != ":"
        and statement.nb_tokens >= 3
        and statement.bad_token != statement.tokens[2]
    ):
        return {}

    new_statement = fixers.modify_token(
        statement.tokens, statement.bad_token, prepend="()"
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

    if statement.bad_token_index != 2 and statement.last_token != ":":
        return {}

    new_statement = fixers.replace_two_tokens(
        statement.tokens,
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
def keyword_as_function_name(statement):
    # Something like
    # def pass() ...
    _ = current_lang.translate
    if not (
        statement.bad_token.is_keyword()
        and statement.prev_token == statement.first_token
    ):
        return {}

    hint = _("You cannot use a Python keyword as a function name.\n")
    cause = _(
        "You tried to use the Python keyword `{kwd}` as a function name.\n"
    ).format(kwd=statement.bad_token)

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if not fixers.check_statement(new_statement):
        cause += "\n" + _("There are more syntax errors later in your code.\n")

    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def other_invalid_function_names(statement):
    _ = current_lang.translate

    if statement.bad_token.is_identifier() or not (
        statement.prev_token == statement.first_token
    ):
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
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
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def function_definition_missing_name(statement):
    _ = current_lang.translate
    if not (
        statement.first_token == "def"
        and statement.bad_token == "("
        and statement.prev_token == statement.first_token
    ):
        return {}

    cause = _("You forgot to name your function.\n") + def_correct_syntax()
    return {"cause": cause}


@add_statement_analyzer
def keyword_not_allowed_as_function_argument(statement):
    _ = current_lang.translate
    if not (statement.bad_token.is_keyword() and statement.begin_brackets):
        return {}

    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if not fixers.check_statement(new_statement):
        return {}

    cause = _(
        "I am guessing that you tried to use the Python keyword\n"
        "`{kwd}` as an argument in the definition of a function\n"
        "where an identifier (variable name) was expected.\n"
    ).format(kwd=statement.bad_token)

    return {"cause": cause}


@add_statement_analyzer
def def_begin_code_block(statement):
    # Thinking of trying to use def to begin a code block, i.e.
    # def : ...
    _ = current_lang.translate
    if statement.first_token != "def" or statement.bad_token != ":":
        return {}

    if not statement.prev_token == statement.first_token:
        return {}

    if statement.first_token.start_col == 0:
        cause = _(
            "You tried to define a function and did not use the correct syntax.\n"
        )
    else:
        cause = _(
            "You tried to define a function or method and did not use the correct syntax.\n"
        )
    cause += def_correct_syntax()

    return {"cause": cause}


@add_statement_analyzer
def dotted_name_no_allowed(statement):
    _ = current_lang.translate
    if statement.bad_token != ".":
        return {}

    if statement.bad_token_index > 3:
        cause = _("You cannot use dotted names as function arguments.\n")
    else:
        cause = _("You cannot use dots in function names.\n")
    return {"cause": cause, "suggest": cause}


@add_statement_analyzer
def positional_arguments_in_def(statement):
    _ = current_lang.translate

    if statement.bad_token != "/":
        return {}

    # TODO: check Python version. / not allowed prior to 3.8 I believe...

    prev_tok = ""
    for tok in statement.tokens:
        # TODO: revise this
        if tok == "*":  # might be incorrect if used in *args
            cause = _(
                "`/` indicates that the previous arguments in a function definition\n"
                "are positional arguments. However, `*` indicates that the arguments\n"
                "that follow must be keyword arguments.\n"
                "When they are used together, `/` must appear before `*`.\n"
            )
            hint = _("`*` must appear after `/` in a function definition.\n")
            return {"cause": cause, "suggest": hint}
        elif tok is statement.bad_token:
            break
        elif tok == "/" and prev_tok == ",":
            cause = _("You can only use `/` once in a function definition.\n")
            return {"cause": cause}
        prev_tok = tok
    return {}


@add_statement_analyzer
def keyword_arguments_in_def(statement):
    _ = current_lang.translate

    if not (statement.bad_token == "*" and statement.first_token == "def"):
        return {}

    prev_tok = ""
    for tok in statement.tokens:
        if tok is statement.bad_token:
            break
        elif tok == "*" and prev_tok == ",":
            cause = _("You can only use `*` once in a function definition.\n")
            return {"cause": cause}
        prev_tok = tok
    return {}


@add_statement_analyzer
def number_as_argument(statement):
    _ = current_lang.translate

    if not statement.bad_token.is_number():
        return {}

    # TODO: add tests
    hint = _("You cannot use a number here.\n")
    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if fixers.check_statement(new_statement):
        cause = _(
            "You used a number as an argument when defining a function.\n"
            "You can only use identifiers (variable names) as function arguments.\n"
        )
        return {"cause": cause, "suggest": hint}
    new_tokens = []
    for index, tok in enumerate(statement.statement_tokens):
        if tok.is_number():
            tok.string = "__name" + str(index)  # could be made more robust
        new_tokens.append(tok)

    new_statement = token_utils.untokenize(new_tokens).strip()
    if fixers.check_statement(new_statement):
        cause = _(
            "You used numbers as arguments when defining a function.\n"
            "You can only use identifiers (variable names) as function arguments.\n"
        )
        return {"cause": cause, "suggest": hint}

    cause = _(
        "I suspect that you used a number as an argument when defining a function.\n"
        "You can only use identifiers (variable names) as function arguments.\n"
        "However, there might be other syntax errors in your function definition.\n"
    )
    return {"cause": cause, "suggest": hint}


@add_statement_analyzer
def string_as_argument(statement):
    _ = current_lang.translate

    if not statement.bad_token.is_string():
        return {}

    # TODO: add tests
    hint = _("You cannot use a string here.\n")
    new_statement = fixers.replace_token(statement.tokens, statement.bad_token, "name")
    if fixers.check_statement(new_statement):
        cause = _(
            "You used a string as an argument when defining a function.\n"
            "You can only use identifiers (variable names) as function arguments.\n"
        )
        return {"cause": cause, "suggest": hint}
    new_tokens = []
    for index, tok in enumerate(statement.tokens):
        if tok.is_string():
            tok.string = "__name" + str(index)  # could be made more robust
        new_tokens.append(tok)

    new_statement = token_utils.untokenize(new_tokens).strip()
    if fixers.check_statement(new_statement):
        cause = _(
            "You used strings as arguments when defining a function.\n"
            "You can only use identifiers (variable names) as function arguments.\n"
        )
        return {"cause": cause, "suggest": hint}

    cause = _(
        "I suspect that you used a string as an argument when defining a function.\n"
        "You can only use identifiers (variable names) as function arguments.\n"
        "However, there might be other syntax errors in your function definition.\n"
    )
    return {"cause": cause, "suggest": hint}
