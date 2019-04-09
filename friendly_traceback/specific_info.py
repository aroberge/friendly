"""specific_info.py

Attempts to provide some specific information about the cause
of a given exception.
"""
import os

'''Note for later

Syntax error contains:
    filename = exc_value.filename
    lineno = str(exc_value.lineno)
    text = exc_value.text
    offset = exc_value.offset
    msg = exc_value.msg
IndentationError and TabError are subclasses of SyntaxError.
'''


def name_error(etype, value):
    return _("        In your program, the unknown name is '{var_name}'.\n").format(
        var_name=str(value).split("'")[1]
    )


def indentation_error(etype, value):
    filename = os.path.basename(value.filename)
    info = _("\n"
             "        Line {linenumber}: {code}\n"
             "        File: {filename}\n").format(
        linenumber=value.lineno, code=value.text, filename=filename
    )

    value = str(value)
    if "unexpected indent" in value:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "        is more indented than expected and does not match\n"
            "        the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "        was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "        is less indented the preceding one, and is not aligned\n"
            "        vertically with another block of code.\n"
        )
    return info + "\n" + this_case


get_cause = {"NameError": name_error, "IndentationError": indentation_error}
