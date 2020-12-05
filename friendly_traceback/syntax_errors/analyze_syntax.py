"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.
"""


from friendly_traceback.my_gettext import current_lang
from friendly_traceback.source_cache import cache
from friendly_traceback.path_info import path_utils
from . import source_analyzer
from . import line_analyzer
from . import message_analyzer


def set_cause_syntax(etype, value, info):
    """Sets the cause"""
    process_parsing_error(etype, value, info)
    return get_likely_cause(etype, value, info)


def get_likely_cause(etype, value, info):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    if etype.__name__ == "IndentationError":
        cause, hint = indentation_error_cause(value)
    elif etype.__name__ == "TabError":
        cause, hint = None, None
    else:
        cause, hint = syntax_error_cause(value, info)
    return cause, hint


def process_parsing_error(etype, value, info):
    _ = current_lang.translate
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    partial_source, _ignore = cache.get_formatted_partial_source(
        filepath, linenumber, offset
    )
    if "-->" in partial_source:
        info["parsing_error"] = _(
            "Python could not understand the code in the file\n"
            "'{filename}'\n"
            "beyond the location indicated by --> and ^.\n"
        ).format(filename=path_utils.shorten_path(filepath))
    elif "unexpected EOF while parsing" in repr(value):
        info["parsing_error"] = _(
            "Python could not understand the code the file\n"
            "'{filename}'.\n"
            "It reached the end of the file and expected more content.\n"
        ).format(filename=path_utils.shorten_path(filepath))
    else:
        info["parsing_error"] = _(
            "Python could not understand the code in the file\n"
            "'{filename}'\n"
            "for an unspecified reason.\n"
        ).format(filename=path_utils.shorten_path(filepath))

    info["parsing_error_source"] = f"{partial_source}\n"


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
    return this_case, None


def syntax_error_cause(value, info):
    """Given some source code as a list of lines, a linenumber
    (starting at 1) indicating where a SyntaxError was detected,
    a message (which follows SyntaxError:) and an offset,
    this attempts to find a probable cause for the Syntax Error.
    """
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    source_lines = cache.get_source_lines(filepath)
    return _find_likely_cause(source_lines, linenumber, message, offset, info)


def _find_likely_cause(source_lines, linenumber, message, offset, info):
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
        offending_line = source_lines[linenumber - 1]
    else:
        offending_line = info["bad_line"]
        source_lines = [offending_line]  # create a fake file for analysis
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this will yield to the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    if "invalid syntax" not in message:  # include f-string: invalid syntax
        cause, hint = message_analyzer.analyze_message(
            message=message,
            line=line,
            linenumber=linenumber,
            source_lines=source_lines,
            offset=offset,
        )
        if cause:
            if hint:
                info["suggest"] = hint
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
        if hint:
            info["suggest"] = hint
        return notice + cause, hint

    # TODO: check to see if the offset correponds to the first token
    # of a line; if so, the error might be found by looking at the
    # previous line.

    # Failing that, we look for another type of common mistake. Note that
    # while we look for missing or mismatched brackets, such as (],
    # we also can sometimes identify other problems during this step.

    cause = source_analyzer.scan_source(source_lines, linenumber, offset, info=info)
    if cause:
        if "suggest" in info:
            hint = info["suggest"]
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
