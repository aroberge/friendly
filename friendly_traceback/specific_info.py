"""specific_info.py

Attempts to provide some specific information about the cause
of a given exception.
"""


def name_error(etype, value):

    return _("        In your program, the unknown name is '{var_name}'.\n").format(
        var_name=value.split("'")[1]
    )


def indentation_error(etype, value):
    if "unexpected indent" in value:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "    is more indented than expected and does not match\n"
            "    the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "    was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "        In this case, the line identified in the file above\n"
            "    is less indented the preceding one, and is not aligned\n"
            "    ertically with another block of code.\n"
        )
    return this_case


get_cause = {"NameError": name_error, "IndentationError": indentation_error}
