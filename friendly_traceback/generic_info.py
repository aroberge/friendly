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


def syntax_error(*args):
    _ = current_lang.lang
    return _(
        "    A SyntaxError occurs when Python cannot understand your code.\n"
        "    There could be many possible reasons:\n"
        "    - a keyword might be misspelled;\n"
        "    - a colon, :, or some other symbol like (, ], etc., might be missing;\n"
        "    - etc.\n"
    )


def tab_error(*args):
    _ = current_lang.lang
    return _(
        "    A TabError indicates that you have used both spaces\n"
        "    and tab characters to indent your code.\n"
        "    This is not allowed in Python.\n"
        "    Indenting your code means to have block of codes aligned vertically\n"
        "    by inserting either spaces or tab characters at the beginning of lines.\n"
        "    Python's recommendation is to always use spaces to indent your code.\n"
    )


def unknown(*args):
    _ = current_lang.lang
    return _("    No information is known about this exception.\n")


generic = {
    "IndentationError": indentation_error,
    "NameError": name_error,
    "SyntaxError": syntax_error,
    "TabError": tab_error,
    "Unknown": unknown,
}
