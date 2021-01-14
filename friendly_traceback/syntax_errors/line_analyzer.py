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
