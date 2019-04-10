"""formatter.py

First version - needs to be documented.
"""
import inspect
import os

from .generic_info import generic
from .specific_info import get_cause

CONTEXT = 4


def explain_traceback(etype, value, tb):
    result = []

    result.append(provide_generic_explanation(etype.__name__, value))
    cause = get_likely_cause(etype, value)
    if cause is not None:
        result.append(cause)

    records = inspect.getinnerframes(tb, CONTEXT)

    _frame, filename, linenumber, _func, lines, index = records[0]  # last call
    info = get_source_info(filename, linenumber, lines, index)
    result.append(add_source_info(info))

    if len(records) > 1:
        _frame, filename, linenumber, _func, lines, index = records[-1]  # origin
        info = get_source_info(filename, linenumber, lines, index)
        result.append(add_source_info(info, last_call=False))

    return "\n".join(result)


def provide_generic_explanation(name, value):
    """Provides a generic explanation about a particular
       error.
    """
    if name in generic:
        explanation = generic[name]()
    else:
        explanation = generic["Unknown"]()
    # fmt: off
    return _(
        "\n"
        "    Python exception: \n"
        "        {name}: {value}\n"
        "\n"
        "{explanation}"
    ).format(name=name, value=value, explanation=explanation)
    # fmt: on


def get_likely_cause(etype, value):
    if etype.__name__ in get_cause:
        return get_cause[etype.__name__](etype, value)
    else:
        return None


def get_source_info(filename, linenumber, lines, index):
    if filename and os.path.abspath(filename):
        filename = os.path.basename(filename)
    elif not filename:
        return None
    if index is not None:
        source = highlight_source(linenumber, index, lines)
    else:
        return None

    return {"filename": filename, "source": source, "linenumber": linenumber}


def add_source_info(info, last_call=True):

    if last_call:
        message = _(
            "\n"
            "    Execution stopped on line {linenumber} of file '{filename}'.\n"
            "\n"
            "{source}\n"
        ).format(**info)

    else:
        message = _(
            "\n"
            "    Exception raised  on line {linenumber} of file '{filename}'.\n"
            "\n"
            "{source}\n"
        ).format(**info)

    return message


def highlight_source(linenumber, index, lines):
    """Displays a few relevant lines from a file, showing line numbers
       and identifying a particular line.
    """
    new_lines = []
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits
    i = linenumber - index
    for line in lines:
        if i == linenumber:
            num = with_mark.format(i)
        else:
            num = no_mark.format(i)
        new_lines.append(num + line.rstrip())
        i += 1
    return "\n".join(new_lines)
