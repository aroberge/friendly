"""This module look for various errors in the entire source.

Most of these errors are connected with parenthesis, (),
square brackets, [], and curly brackets, {}.

The type of errors it can look for are:

    1. mismatched brackets
    2. missing closing bracket
    3. missing comma between items.
    4. using = instead of : in a dict


This module started with a single function, which grew as it tried to figure out
the cause of the SyntaxError in a single pass through the source code.
While this might be more "efficient", it made the logic a lot more
difficult to understand.

In the interest of simplicity, extensibility and maintainability,
we now have multiple functions, some of which have almost identical
chunks of code.
"""
from .syntax_utils import matching_brackets, name_bracket, no_unclosed_brackets

from .. import debug_helper
from ..my_gettext import current_lang

from .. import token_utils


def scan_source(source_lines=None, linenumber=0, offset=0):
    """Scans the entire source, looking at possible causes of
    SyntaxError: invalid syntax
    """
    if not source_lines:
        return
    source = "".join(source_lines)
    source_tokens = token_utils.get_significant_tokens(source)
    cause = look_for_mismatched_brackets(
        source_tokens=source_tokens,
        source_lines=source_lines,
        max_linenumber=linenumber,
        offset=offset,
    )
    if cause:
        return cause
    cause = look_for_missing_bracket(
        source_tokens=source_tokens,
        source_lines=source_lines,
        max_linenumber=linenumber,
        offset=offset,
    )
    if cause:
        return cause


def look_for_mismatched_brackets(
    *, source_tokens=None, source_lines=None, max_linenumber=None, offset=None
):
    _ = current_lang.translate
    if source_tokens is None:
        source = "".join(source_lines)
        source_tokens = token_utils.get_significant_tokens(source)

    brackets = []
    for token in source_tokens:
        if (
            token.start_row == max_linenumber
            and token.start_col > offset
            or token.start_row > max_linenumber
        ):
            return

        if token.is_not_in("()[]}{"):
            continue
        if token.is_in("([{"):
            brackets.append((token.string, token.start_row, token.start_col))
        elif token.is_in(")]}"):
            # In some of the cases below, we include the offending lines at the
            # bottom of the error message as they might not be shown in the
            # partial source included in the traceback.
            if not brackets:
                bracket = name_bracket(token)
                _lineno = token.start_row
                _source = f"\n    {_lineno}: {source_lines[_lineno - 1]}"
                shift = len(str(_lineno)) + token.start_col + 6
                _source += " " * shift + "^\n"
                return (
                    _(
                        "The closing {bracket} on line {linenumber}"
                        " does not match anything.\n"
                    ).format(bracket=bracket, linenumber=token.start_row)
                    + _source
                )
            else:
                open_bracket, open_lineno, open_col = brackets.pop()
                if not matching_brackets(open_bracket, token):
                    bracket = name_bracket(token)
                    open_bracket = name_bracket(open_bracket)
                    _source = f"\n    {open_lineno}: {source_lines[open_lineno - 1]}"
                    shift = len(str(open_lineno)) + open_col + 6
                    if open_lineno == token.start_row:
                        _source += " " * shift + "^"
                        shift = token.start_col - open_col - 1
                        _source += " " * shift + "^\n"
                    else:
                        _source += " " * shift + "^\n"
                        _lineno = token.start_row
                        _source += f"    {_lineno}: {source_lines[_lineno - 1]}"
                        shift = len(str(_lineno)) + token.start_col + 6
                        _source += " " * shift + "^\n"
                    return (
                        _(
                            "The closing {bracket} on line {close_lineno} does not match "
                            "the opening {open_bracket} on line {open_lineno}.\n"
                        ).format(
                            bracket=bracket,
                            close_lineno=token.start_row,
                            open_bracket=open_bracket,
                            open_lineno=open_lineno,
                        )
                        + _source
                    )


# TODO: refactor this
def look_for_missing_bracket(
    *, source_tokens=None, source_lines=None, max_linenumber=None, offset=None
):
    """This function was initially looking for missing or mismatched brackets
    but it has expanded to include other cases.  By brackets here, we mean
    any one of: ()[]{}.

    We have a few cases to consider:

    1. mismatched brackets
    2. missing closing bracket
    3. missing comma between items.
    4. using = instead of : in a dict

    The last two cases will often result in an error being flagged at
    a given location such that the code up to that point would have
    an unclosed bracket.  For example, case 4 could be:

        ages = {'Alice' = 22, ...
                        ^

    and we would have an unclosed {.
    """
    _ = current_lang.translate
    if source_tokens is None:
        source = "".join(source_lines)
        source_tokens = token_utils.get_significant_tokens(source)
    brackets = []
    will_be_previous = None
    previous_token = None

    for token in source_tokens:
        if will_be_previous is not None:
            previous_token = will_be_previous

        if not token.string:
            continue
        will_be_previous = token

        if (
            token.start_row == max_linenumber
            and token.start_col >= offset
            or token.start_row > max_linenumber
        ):
            # We are beyond the location flagged by Python;
            if (previous_token == "=" or token == "=") and brackets:
                _open_bracket, _start_row, _start_col = brackets.pop()
                if _open_bracket == "{":
                    return _(
                        "It is possible that "
                        "you used an equal sign `=` instead of a colon `:`\n"
                        "to assign values to keys in a dict\n"
                        "before or at the position indicated by --> and ^.\n"
                    )
                else:
                    brackets.append((_open_bracket, _start_row, _start_col))
            break

        # We are not beyond the location flagged by Python
        if token.is_not_in("()[]}{"):
            continue
        if token.is_in("([{"):
            brackets.append((token.string, token.start_row, token.start_col))
        elif token.is_in(")]}"):
            # In some of the cases below, we include the offending lines at the
            # bottom of the error message as they might not be shown in the
            # partial source included in the traceback.
            if not brackets:
                debug_helper.log("source_analyzer.look_for_missing_bracket()")
                debug_helper.log("No brackets remain.")
                return False
            else:
                open_bracket, open_lineno, open_col = brackets.pop()
                if not matching_brackets(open_bracket, token):
                    debug_helper.log("source_analyzer.look_for_missing_bracket()")
                    debug_helper.log("No matching bracket.")
                    return False

    if brackets:
        bracket, linenumber, start_col = brackets.pop()

        bracket_name = name_bracket(bracket)
        _source = f"\n    {linenumber}: {source_lines[linenumber - 1]}"
        shift = len(str(linenumber)) + start_col + 6
        _source += " " * shift + "|\n"

        cause = (
            _("The opening {bracket} on line {linenumber} is not closed.\n").format(
                bracket=bracket_name, linenumber=linenumber
            )
            + _source
        )

        if no_unclosed_brackets(source_tokens) and (
            previous_token.is_number()
            or previous_token.is_identifier()
            or previous_token.is_string()
        ):
            if bracket == "(":
                return cause + _(
                    "It is also possible that you "
                    "forgot a comma between items in a tuple, \n"
                    "or between function arguments, \n"
                    "before the position indicated by --> and ^.\n"
                )
            elif bracket == "[":
                return cause + _(
                    "It is also possible that you "
                    "forgot a comma between items in a list\n"
                    "before the position indicated by --> and ^.\n"
                )
            else:
                return cause + _(
                    "It is also possible that you "
                    "forgot a comma between items in a set or dict\n"
                    "before the position indicated by --> and ^.\n"
                )
        return cause
    else:
        return False


def isolate_bad_statement(*, source_lines=None, linenumber=None, offset=0):
    """This function scans the source searching for the statement that
    caused the problem. Most often, it will be a single line of code. However,
    sometimes it might be a multiline statement that includes code surrounded
    by some brackets spanning multiple lines.

    linenumber is the line number identified by Python as containing the error.

    It returns a tuple containing three items:
    1. a list of tokens for that statement
    2. a list of opening brackets that are part of that statement and have
       not yet been closed
    3. an unmatched closing bracket or None
    """
    _ = current_lang.translate
    if linenumber is None:  # can happen with Too many nested blocks error
        return [], [], None, None

    offset -= 1  # shift for proper comparison
    source = "".join(source_lines)
    source_tokens = token_utils.tokenize(source)

    bad_token = None
    end_bracket = None
    begin_brackets = []
    statement_tokens = []
    previous_row = -1
    previous_token = None
    continuation_line = False

    for token in source_tokens:
        # is this a new statement?
        if token.start_row > previous_row:
            if previous_token is not None:
                continuation_line = previous_token.line.endswith("\\\n")
            if token.start_row <= linenumber and not begin_brackets:
                statement_tokens = []
            previous_row = token.start_row

        # Did we collect all the tokens belonging to the statement?
        if (
            token.start_row > linenumber
            and not begin_brackets
            and not continuation_line
        ):
            break

        statement_tokens.append(token)
        # TODO: check to ensure that this works with all Python versions.
        # The offset seems to be different depending on Python versions, something matching
        # the beginning of a token, sometimes the end.
        if (
            token.start_row == linenumber
            and token.start_col >= offset
            and bad_token is not None
        ):
            bad_token = token
        previous_token = token
        if token.is_not_in("()[]}{"):
            continue

        if token.is_in("([{"):
            begin_brackets.append(token)
        elif token.is_in(")]}"):  # Does it match or not
            end_bracket = token
            if not begin_brackets:
                break
            else:
                open_bracket = begin_brackets.pop()
                if not matching_brackets(open_bracket, token):
                    begin_brackets.append(open_bracket)
                    break
                else:
                    end_bracket = None

    return statement_tokens, begin_brackets, end_bracket, bad_token
