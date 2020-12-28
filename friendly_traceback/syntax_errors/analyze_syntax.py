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


def set_cause_syntax(etype, value, tb_data):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    cause = hint = None
    try:
        if etype.__name__ == "IndentationError":
            cause = indentation_error_cause(tb_data.value)
        elif etype.__name__ == "TabError":
            pass  # No need to provide additional information
        else:
            cause, hint = find_syntax_error_cause(tb_data)
    except Exception as e:
        debug_helper.log("Exception caught in set_cause_syntax().")
        debug_helper.log(repr(e))
        cause = _(
            "Exception raised by Friendly-traceback itself.\n"
            "Please report this example to\n"
            "https://github.com/aroberge/friendly-traceback/issues\n"
        )
    return cause, hint


def indentation_error_cause(value):
    _ = current_lang.translate

    value = str(value)
    if "unexpected indent" in value:
        this_case = _(
            "In this case, the line identified above\n"
            "is more indented than expected and \n"
            "does not match the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "In this case, the line identified above\n"
            "was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "In this case, the line identified above is\n"
            "less indented than the preceding one,\n"
            "and is not aligned vertically with another block of code.\n"
        )
    return this_case


def find_syntax_error_cause(tb_data):
    """Attempts to find the cause of a SyntaxError
    """
    value = tb_data.value
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    source_lines = cache.get_source_lines(filepath)

    # We use this indirect method with explicit arguments to make easier
    # to write unit tests.
    return _find_likely_cause(source_lines, linenumber, message, offset, tb_data)


def _find_likely_cause(source_lines, linenumber, message, offset, tb_data=None):
    """Given some source code as a list of lines, a linenumber
    (starting at 1) indicating where a SyntaxError was detected,
    a message (which follows SyntaxError:) and an offset,
    this attempts to find a probable cause for the Syntax Error.
    """
    _ = current_lang.translate
    hint = None

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
        if linenumber is None:  # can happen in some rare cases
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

    # If not cause has been identified, we look at a single line
    # where the error has been found by Python, and try to find the source
    # of the error

    cause, hint = line_analyzer.analyze_last_line(line, offset=offset)
    if cause:
        return notice + cause, hint

    # TODO: check to see if the offset correponds to the first token
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
