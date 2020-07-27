"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.
"""


from .my_gettext import current_lang
from .source_cache import cache
from . import source_analyzer
from . import line_analyzer
from . import message_analyzer


def find_likely_cause(value):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    source_lines = cache.get_source(filepath)
    if not source_lines and filepath == "<stdin>":
        source_lines = [""]
        linenumber = 1
    return _find_likely_cause(source_lines, linenumber, message, offset)


def _find_likely_cause(source_lines, linenumber, message, offset):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    _ = current_lang.translate

    offending_line = source_lines[linenumber - 1]
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this will yield to the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    if message != "invalid syntax":
        cause = message_analyzer.analyze_message(
            message=message,
            line=line,
            linenumber=linenumber,
            source_lines=source_lines,
            offset=offset,
        )
        if cause:
            return cause
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

    cause = line_analyzer.analyze_last_line(line, offset=offset)
    if cause:
        return notice + cause

    # TODO: check to see if the offset correponds to the first token
    # of a line; if so, the error might be found by looking at the
    # previous line.

    # Failing that, we look for another type of common mistake. Note that
    # while we look for missing or mismatched brackets, such as (],
    # we also can sometimes identify other problems during this step.

    cause = source_analyzer.scan_source(source_lines, linenumber, offset)
    if cause:
        return notice + cause

    # Eventually, we might add another step that looks at the entire code
    # For now, we just stop here

    return _(
        "Currently, I cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "You might want to report this case to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
    )
