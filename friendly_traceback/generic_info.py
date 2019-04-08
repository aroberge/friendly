"""Basic information about Python exceptions"""


def name_error(*args):
    return _(
        "    A NameError exception indicates that a variable or\n"
        "    function name is not known to Python.\n"
        "    Most often, this is because there is a spelling mistake.\n"
        "    However, sometimes it is because the name is used\n"
        "    before being defined or given a value.\n"
    )


def unknown(*args):
    return _("    No information is known about this exception.\n")


generic = {"NameError": name_error, "Unknown": unknown}
