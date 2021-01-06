"""This module contains functions that are used to
   analyze a single line of code which has been identified
   as containing a syntax error with the message "invalid syntax".
"""
import keyword

from . import syntax_utils
from .. import debug_helper
from .. import utils
from ..my_gettext import current_lang

from .. import token_utils


def is_potential_statement(tokens):
    """This helper function tests the list of tokens
       (usually corresponding to a single line of code)
       and returns True if the corresponding line of code could possibly be a
       complete Python statement as described below.

       A complete Python statement would have brackets,
       including (), [], and {}, matched in pairs,
       and would not end with the continuation character.
    """
    line = tokens[0].line

    # All tokens passed should come from the same line of code
    if tokens[-1].line != line:
        debug_helper.log("In line_analyzer.is_potential_statement()")
        debug_helper.log("Not all tokens came from the same line.")
        return False

    if line.endswith("\\") or line.endswith("\\\n"):
        return False

    return syntax_utils.no_unclosed_brackets(tokens)


LINE_ANALYZERS = []


def add_line_analyzer(func):
    """A simple decorator that adds a function to the list
    of all functions that analyze a single line of code."""
    LINE_ANALYZERS.append(func)

    def wrapper(tokens, offset=None):
        return func(tokens, offset=offset)

    return wrapper


# ========================================================
# Main calling function
# ========================================================


def analyze_last_line(line, offset=None):
    """Analyzes the last line of code as identified by Python as that
    on which the error occurred."""
    tokens = token_utils.get_significant_tokens(
        line
    )  # tokens do not include spaces nor comments

    if not tokens:
        return None, None

    for analyzer in LINE_ANALYZERS:
        cause, hint = analyzer(tokens, offset=offset)
        if cause:
            return cause, hint
    return None, None


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order can yield incorrect results
# ==================


@add_line_analyzer
def invalid_name(tokens, **_kwargs):
    """Identifies invalid identifiers when a name begins with a number"""
    _ = current_lang.translate
    cause = hint = None

    if len(tokens) < 2:
        return cause, hint

    note = None
    for first, second in zip(tokens, tokens[1:]):
        if first.is_number() and second.is_identifier() and first.end == second.start:
            cause = _("Valid names cannot begin with a number.\n")
            if first.is_complex():
                note = _("[Note: `{first}` is a complex number.]\n").format(first=first)
                second.string = first.string[-1] + second.string
                first.string = first.string[:-1]
            if second == "i" and first != tokens[0]:
                hint = _("Did you mean `{number}j`?\n").format(number=first)
                cause += _(
                    "Perhaps you thought that `i` could be used to represent\n"
                    "the square root of -1. In Python, `j` (or `1j`) is used for this\n"
                    "and perhaps you meant to write `{number}j`.\n"
                ).format(number=first)
                return cause, hint
            break

    # Try to distinguish between  "2x = ... and y = ... 2x ..."
    if cause:
        tokens.append(";")
        for first, second, third in zip(tokens, tokens[1:], tokens[2:]):
            if (
                first.is_number()
                and second.is_identifier()
                and first.end == second.start
            ):
                if third != "=":
                    hint = _(
                        "Perhaps you forgot a multiplication operator,"
                        " `{first} * {second}`.\n"
                    ).format(first=first, second=second)
                    cause = cause + hint
                else:
                    hint = cause
                break
    if note is not None:
        cause += "\n" + note
    return cause, hint


def _add_operator(tokens, first):
    first_string = first.string
    results = []
    for operator in " +", " -", " *", ",", " in":
        if operator == " in" and results:
            break
        new_tokens = []
        for tok in tokens:
            if tok == first:
                tok.string = tok.string + operator
            new_tokens.append(tok)
        line = token_utils.untokenize(new_tokens).strip()
        if syntax_utils.check_statement(line):
            if operator == "," and results:  # So that it prints correctly
                operator = '","'
            results.append((operator.strip(), line))
        first.string = first_string

    return results


def perhaps_misspelled_keyword(tokens, first, second):
    kwlist = keyword.kwlist
    similar = utils.get_similar_words(first.string, kwlist)
    similar += utils.get_similar_words(second.string, kwlist)
    words = [word for word in kwlist if word not in similar]
    similar.extend(words)
    results = []
    for wrong in (first, second):
        original_string = wrong.string
        for word in similar:
            if results:
                continue
            new_tokens = []
            for tok in tokens:
                if tok == wrong:
                    tok.string = word
                new_tokens.append(tok)
            line = token_utils.untokenize(new_tokens).strip()
            if syntax_utils.check_statement(line):
                results.append((word, line))
            wrong.string = original_string
    # The with keyword can appear in similar situations as for/in and others.
    if len(results) > 1:
        results = [(word, line) for word, line in results if word != "with"]
    return results


@add_line_analyzer
def missing_comma_or_operator(tokens, offset=None):
    """Check to see if a comma or other operator
    is possibly missing between identifiers, or numbers, or both.
    """
    _ = current_lang.translate
    cause = hint = None

    if len(tokens) < 2:
        return cause, hint

    for first, second in zip(tokens, tokens[1:]):
        if (
            first.is_number()
            and not first.is_complex()  # should not be needed as the preceding
            # function should have caught this.
            and second == "i"
            and first.end == second.start
        ):
            hint = _("Did you mean `{number}j`?\n").format(number=first)
            cause = (
                "Perhaps you thought that `i` could be used to represent\n"
                "the square root of -1.\n"
                "In Python, `j` immediately following a number is used for this.\n"
                "Perhaps you meant to write `{number}j`.\n"
            ).format(number=first)
            return cause, hint
        if (
            (first.is_number() or first.is_identifier() or first.is_string())
            and (second.is_number() or second.is_identifier() or second.is_string())
            and second.start_col <= offset <= second.end_col
        ):
            cause = _(
                "Python indicates that the error is caused by "
                "`{second}` written immediately after `{first}`.\n"
            ).format(first=first, second=second)
            results = _add_operator(tokens, first)
            if results:
                if len(results) == 1:
                    operator, line = results[0]
                    hint = _("Did you mean `{line}`?\n").format(line=line)
                    cause += _(
                        "Perhaps you meant to write `{operator}` between\n"
                        "`{first}` and `{second}`:\n\n"
                        "    {line}\n"
                        "which would not cause a `SyntaxError`.\n"
                    ).format(first=first, second=second, line=line, operator=operator)
                else:
                    operators = [operator for operator, line in results]
                    lines = [line for operator, line in results]

                    hint = _(
                        "Did you forget something between `{first}` and `{second}`?\n"
                    ).format(first=first, second=second)

                    cause += _(
                        "Perhaps you meant to insert an operator like `{operators}`\n"
                        "between `{first}` and `{second}`.\n"
                        "The following lines of code would not cause any `SyntaxError`:\n\n"
                    ).format(
                        first=first,
                        second=second,
                        operators=utils.list_to_string(operators),
                    )
                    for line in lines:
                        cause += f"    {line}\n"

                    cause += _("Note: these are just some of the possible choices.\n")
            else:
                # Add case here where we replace either first or second by a Python keyword
                results = perhaps_misspelled_keyword(tokens, first, second)
                if results:
                    if len(results) == 1:
                        word, line = results[0]
                        hint = _("Did you mean `{line}`?\n").format(line=line)

                        cause += _(
                            "Perhaps you meant to write `{keyword}` and made a typo.\n"
                            "The correct line would then be `{line}`\n"
                        ).format(keyword=word, line=line)
                    else:
                        lines = [line for _word, line in results]
                        hint = _("Did you mean `{line}`?\n").format(line=lines[0])

                        cause += _(
                            "Perhaps you wrote another word instead of a Python keyword.\n"
                            "If that is the case, perhaps you meant to write one of\n"
                            "the following lines of code which would not raise a `SyntaxError`:\n\n"
                        )
                        for line in lines:
                            cause += f"    {line}\n"

                else:
                    cause = _(
                        "Perhaps you forgot to write something between `{first}` and `{second}`\n"
                    ).format(first=first, second=second)

            if first == tokens[0]:
                first_tokens = []
                line = None
                for tok in tokens:
                    if tok == "=":
                        line = token_utils.untokenize(tokens)
                        begin, end = line.split("=", 1)
                        line = "_".join(first_tokens) + " =" + end
                        cause += (
                            "\n"
                            + _(
                                "Or perhaps you forgot that you cannot have spaces\n"
                                "in variable names.\n"
                            )
                            + f"\n\n    {line}\n"
                        )
                        break
                    elif not tok.is_identifier():
                        break
                    else:
                        first_tokens.append(tok.string)
                if line:
                    hint = _("Did you mean `{line}`?\n").format(line=line)
            return cause, hint
    return cause, hint


@add_line_analyzer
def malformed_def(tokens, **_kwargs):
    """Looks for problems with defining a function, assuming that
    the information passed looks like a complete statement"""
    _ = current_lang.translate
    cause = hint = None
    if tokens[0] != "def":
        return cause, hint

    if not is_potential_statement(tokens):
        return cause, hint

    if len(tokens) >= 3 and tokens[1].is_identifier() and tokens[2] == ":":
        hint = _("Perhaps you forgot parentheses.\n")
    # need at least five tokens: def name ( ) :
    if (
        len(tokens) < 5
        or not tokens[1].is_name()
        or tokens[2] != "("
        or tokens[-2] != ")"
        or tokens[-1] != ":"
    ):
        name = _("a function or method")
        cause = _(
            "You tried to define {class_or_function} "
            "and did not use the correct syntax.\n"
            "The correct syntax is:\n\n"
            "    def name ( optional_arguments ):"
            "\n"
        ).format(class_or_function=name)
        return cause, hint

    fn_name = tokens[1]
    if fn_name.is_keyword():
        cause = _(
            "You tried to use the Python keyword `{kwd}` as a function name.\n"
        ).format(kwd=fn_name)
        return cause, hint

    # Lets look at the possibility that a keyword might have been used
    # as an argument or keyword argument. The following test is admittedly
    # crude and imperfect, but it is the last one we do.

    prev_token_str = None
    parens = 0
    brackets = 0
    curly = 0
    for index, tok in enumerate(tokens):
        # Note, we know that a SyntaxError: invalid syntax occurred.
        # So, while some cases of the following might be ok, we assume here that
        # they might have caused the error. They might include things like:
        # def test(None ...)  or
        # def test(*None ...) or
        # def test(**None ...) or
        # def test(a, None ...)
        #       but not
        # def test(a=None ...) nor
        # def test(a=(None,...)) nor
        # def test(a = [1, None])
        if tok == "(":
            parens += 1
        elif tok == ")":
            parens -= 1
        elif tok == "[":
            brackets += 1
        elif tok == "]":
            brackets -= 1
        elif tok == "{":
            curly += 1
        elif tok == "}":
            curly -= 1

        elif tok.is_keyword() and (
            (prev_token_str == "(" and index == 3)  # first argument
            or (
                parens % 2 == 1
                and brackets % 2 == 0
                and curly % 2 == 0
                and prev_token_str in [",", "*", "**"]
            )
        ):
            return (
                _(
                    "I am guessing that you tried to use the Python keyword\n"
                    "`{kwd}` as an argument in the definition of a function.\n"
                ).format(kwd=tok),
                None,
            )
            # break
        prev_token_str = tok
    return cause, hint
