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
from friendly_traceback.my_gettext import current_lang
from friendly_traceback import utils
from friendly_traceback.friendly_exception import FriendlyException


def scan_source(source_lines=None, linenumber=0, offset=0):
    """Scans the entire source, looking at possible causes of
       SyntaxError: invalid syntax
    """
    if not source_lines:
        return
    source_tokens = utils.tokenize_source_lines(source_lines)
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
        source_tokens = utils.tokenize_source_lines(source_lines)

    brackets = []
    for token in source_tokens:
        if (
            token.start_line == max_linenumber
            and token.start_col > offset
            or token.start_line > max_linenumber
        ):
            return

        if token.string not in "()[]}{":
            continue
        if token.string in "([{":
            brackets.append((token.string, token.start_line, token.start_col))
        elif token.string in ")]}":
            # In some of the cases below, we include the offending lines at the
            # bottom of the error message as they might not be shown in the
            # partial source included in the traceback.
            if not brackets:
                bracket = name_bracket(token.string)
                _lineno = token.start_line
                _source = f"\n    {_lineno}: {source_lines[_lineno-1]}\n"
                shift = len(str(_lineno)) + token.start_col + 6
                _source += " " * shift + "^\n"
                return (
                    _(
                        "The closing {bracket} on line {linenumber}"
                        " does not match anything.\n"
                    ).format(bracket=bracket, linenumber=token.start_line)
                    + _source
                )
            else:
                open_bracket, open_lineno, open_col = brackets.pop()
                if not matching_brackets(open_bracket, token.string):
                    bracket = name_bracket(token.string)
                    open_bracket = name_bracket(open_bracket)
                    _source = f"\n    {open_lineno}: {source_lines[open_lineno-1]}\n"
                    shift = len(str(open_lineno)) + open_col + 6
                    if open_lineno == token.start_line:
                        _source += " " * shift + "^"
                        shift = token.start_col - open_col - 1
                        _source += " " * shift + "^\n"
                    else:
                        _source += " " * shift + "^\n"
                        _lineno = token.start_line
                        _source += f"    {_lineno}: {source_lines[_lineno-1]}\n"
                        shift = len(str(_lineno)) + token.start_col + 6
                        _source += " " * shift + "^\n"
                    return (
                        _(
                            "The closing {bracket} on line {close_lineno} does not match "
                            "the opening {open_bracket} on line {open_lineno}.\n"
                        ).format(
                            bracket=bracket,
                            close_lineno=token.start_line,
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
        source_tokens = utils.tokenize_source_lines(source_lines)
    brackets = []
    beyond_brackets = []
    end_bracket = None
    will_be_previous = None
    previous_token_string = None

    for token in source_tokens:
        if will_be_previous is not None:
            previous_token_string = will_be_previous

        if not token.string:
            continue
        will_be_previous = token.string

        if (
            token.start_line == max_linenumber
            and token.start_col >= offset
            or token.start_line > max_linenumber
        ):
            # We are beyond the location flagged by Python;
            if previous_token_string == "=" and brackets:
                _open_bracket, _start_line, _start_col = brackets.pop()
                if _open_bracket == "{":
                    return _(
                        "It is possible that "
                        "you used an equal sign `=` instead of a colon `:`\n"
                        "to assign values to keys in a dict\n"
                        "before or at the position indicated by --> and ^.\n"
                    )
                else:
                    brackets.append((_open_bracket, _start_line, _start_col))
            # Perhaps we are simply missing a comma between items.
            # If so, we should be able to find a closing bracket.
            if token.string in "([{":
                beyond_brackets.append(token.string)
            elif token.string in ")]}":
                if len(beyond_brackets) % 2 == 0:
                    end_bracket = token.string
                    break
                else:
                    end_bracket = None
                    open_bracket = beyond_brackets.pop()
                    if not matching_brackets(open_bracket, token.string):
                        break
            continue

        # We are not beyond the location flagged by Python
        if token.string not in "()[]}{":
            continue
        if token.string in "([{":
            brackets.append((token.string, token.start_line, token.start_col))
        elif token.string in ")]}":
            # In some of the cases below, we include the offending lines at the
            # bottom of the error message as they might not be shown in the
            # partial source included in the traceback.
            if not brackets:
                raise FriendlyException("source_analyzer.look_for_missing_bracket")
            else:
                open_bracket, open_lineno, open_col = brackets.pop()
                if not matching_brackets(open_bracket, token.string):
                    raise FriendlyException("source_analyzer.look_for_missing_bracket")

    if brackets:
        bracket, linenumber, start_col = brackets.pop()
        if end_bracket is not None:
            if matching_brackets(bracket, end_bracket):
                if bracket == "(":
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a tuple, \n"
                        "or between function arguments, \n"
                        "before the position indicated by --> and ^.\n"
                    )
                elif bracket == "[":
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a list\n"
                        "before the position indicated by --> and ^.\n"
                    )
                else:
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a set or dict\n"
                        "before the position indicated by --> and ^.\n"
                    )

        bracket = name_bracket(bracket)
        _source = f"\n    {linenumber}: {source_lines[linenumber-1]}\n"
        shift = len(str(linenumber)) + start_col + 6
        _source += " " * shift + "^\n"
        return (
            _("The opening {bracket} on line {linenumber} is not closed.\n").format(
                bracket=bracket, linenumber=linenumber
            )
            + _source
        )
    else:
        return False


def matching_brackets(bra, ket):
    return (
        (bra == "(" and ket == ")")
        or (bra == "[" and ket == "]")
        or (bra == "{" and ket == "}")
    )


def name_bracket(bracket):
    _ = current_lang.translate
    if bracket == "(":
        return _("parenthesis `(`")
    elif bracket == ")":
        return _("parenthesis `)`")
    elif bracket == "[":
        return _("square bracket `[`")
    elif bracket == "]":
        return _("square bracket `]`")
    elif bracket == "{":
        return _("curly bracket `{`")
    elif bracket == "}":
        return _("curly bracket `}`")
    else:  # Should never happen - help for diagnostic
        raise FriendlyException("source_analyzer.name_bracket")
