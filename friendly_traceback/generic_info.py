"""Basic information about Python exceptions"""
from .my_gettext import current_lang


def indentation_error(*args):
    _ = current_lang.lang
    return _(
        "    An IndentationError occurs when a given line of code is\n"
        "    not indented (aligned vertically with other lines) as expected.\n"
    )


def name_error(*args):
    _ = current_lang.lang
    return _(
        "    A NameError exception indicates that a variable or\n"
        "    function name is not known to Python.\n"
        "    Most often, this is because there is a spelling mistake.\n"
        "    However, sometimes it is because the name is used\n"
        "    before being defined or given a value.\n"
    )


def unknown(*args):
    _ = current_lang.lang
    return _("    No information is known about this exception.\n")


generic = {
    "IndentationError": indentation_error,
    "NameError": name_error,
    "Unknown": unknown,
}
