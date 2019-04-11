"""specific_info.py

Attempts to provide some specific information about the cause
of a given exception.
"""
import os


from . import utils
from .my_gettext import current_lang

"""Note for later

Syntax error, and its subclasses, contain:
    filename = exc_value.filename
    lineno = str(exc_value.lineno)
    text = exc_value.text
    offset = exc_value.offset
    msg = exc_value.msg
IndentationError and TabError are subclasses of SyntaxError.
"""


def name_error(etype, value):
    _ = current_lang.lang
    return _("        In your program, the unknown name is '{var_name}'.\n").format(
        var_name=str(value).split("'")[1]
    )


def indentation_error(etype, value):
    _ = current_lang.lang
    filename = value.filename
    linenumber = value.lineno
    offset = value.offset
    source = utils.get_partial_source(filename, linenumber, offset)
    filename = os.path.basename(filename)
    info = _(
        "        Python could not parse the file '{filename}'\n"
        "        beyond the location indicated below by --> and ^.\n"
        "\n"
        "{source}\n"
    ).format(filename=filename, source=source)

    value = str(value)
    if "unexpected indent" in value:
        this_case = _(
            "        In this case, the line identified above\n"
            "        is more indented than expected and \n"
            "        does not match the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "        In this case, the line identified above\n"
            "        was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "        In this case, the line identified above is\n"
            "        less indented than the preceding one,\n"
            "        and is not aligned vertically with another block of code.\n"
        )
    return info + this_case


get_cause = {"NameError": name_error, "IndentationError": indentation_error}