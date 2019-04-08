"""specific_info.py

Attempts to provide some specific information about the cause
of a given exception.
"""


def name_error(etype, value):

    return _("        In your program, the unknown name is '{var_name}'.\n").format(
        var_name=str(value).split("'")[1]
    )


get_cause = {"NameError": name_error}
