"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.

In an ideal world, one would write a custom parser for Python, extending
the existing one with enhanced error messages about where in the parsing
process a SyntaxError occurred, what kind of token was expected, etc.,
and use that information to give feedback to users.

Unfortunately, we do not live in such a world.

Friendly-traceback uses some ad-hoc heuristics to analyze the information
given by Python or the code itself and makes an attempt at guessing
as often as possible what went wrong while trying to avoid giving
incorrect information.
"""

from friendly_traceback.my_gettext import current_lang
from friendly_traceback.source_cache import cache
from . import source_analyzer
from . import line_analyzer
from . import message_analyzer
from .. import debug_helper

import token_utils

# TODO invalid digit '8' in octal literal


def set_cause_syntax(value, tb_data):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    cause = hint = None
    try:
        cause, hint = find_syntax_error_cause(value, tb_data)
    except Exception:
        debug_helper.log_error()
        cause = _(
            "Exception raised by Friendly-traceback itself.\n"
            "Please report this example to\n"
            "https://github.com/aroberge/friendly-traceback/issues\n"
        )
    return cause, hint


def find_syntax_error_cause(value, tb_data):
    """Attempts to find the cause of a SyntaxError"""
    # value = tb_data.value
    _ = current_lang.translate
    cause = hint = None

    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    source_lines = cache.get_source_lines(filepath)

    # SyntaxError in f-strings are handled differently by Python
    # than other types of errors. They are effectively handled internally
    # as special files.  Before Python 3.9, Python will tell us
    # that we have a
    #   SyntaxError: invalid syntax
    # that the error occurred in file <fstring>  (which is not a real file).
    #
    # Starting with Python 3.9, Python will indicates:
    #     SyntaxError: f-string: invalid syntax
    # but will give us the real name of the file.
    #
    # So, given this line with a SyntaxError:
    #   f"{x y}"
    # the traceback will indicate that the error is on line
    #   (x y)
    # which does not correspond to an actual line in the source file
    # that we can retrieve when using Python 3.9.

    if source_lines and "f-string: invalid syntax" not in message:
        if linenumber is None:  # can happen in some rare cases where Python
            # apparently gives up processing a file
            if "too many statically nested blocks" not in message:
                debug_helper.log(
                    "linenumber is None in analyze_syntax._find_likely_cause"
                )
            offending_line = "\n"
            source_lines = ["\n"]
        else:
            offending_line = source_lines[linenumber - 1]
    else:
        offending_line = tb_data.bad_line
        source_lines = [offending_line]  # create a fake file for analysis
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this will yield to the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    if "invalid syntax" not in message:
        cause, hint = message_analyzer.analyze_message(
            message=message,
            line=line,
            linenumber=linenumber,
            source_lines=source_lines,
            offset=offset,
        )
        if cause:
            return cause, hint
        else:
            notice = _(
                "Python gave us the following informative message\n"
                "about the possible cause of the error:\n\n"
                "    {message}\n\n"
                "However, I do not recognize this information and I have\n"
                "to guess what caused the problem, but I might be wrong.\n\n"
            ).format(message=message)
    else:
        notice = _(
            "I make an effort below to guess what caused the problem\n"
            "but I might guess incorrectly.\n\n"
        )

    try:
        tokens, brackets, end_bracket, bad_token = source_analyzer.isolate_bad_statement(
            source_lines=source_lines, linenumber=linenumber, offset=offset
        )
        statement = token_utils.untokenize(tokens)  # noqa
    except Exception:
        debug_helper.log_error()

    # If not cause has been identified, we look at a single line
    # where the error has been found by Python, and try to find the source
    # of the error

    cause, hint = line_analyzer.analyze_last_line(line, offset=offset)
    if cause:
        return notice + cause, hint

    # TODO: check to see if the offset corresponds to the first token
    # of a line; if so, the error might be found by looking at the
    # previous line.

    # Failing that, we look for another type of common mistake. Note that
    # while we look for missing or mismatched brackets, such as (],
    # we also can sometimes identify other problems during this step.

    cause = source_analyzer.scan_source(source_lines, linenumber, offset)
    if cause:
        return notice + cause, hint

    cause = _(
        "Currently, I cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "You might want to report this case to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
    )
    return cause, hint
