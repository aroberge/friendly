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


def unbound_local_error(*args):
    _ = current_lang.lang
    return _(
        "    In Python, variables that are used inside a function are known as \n"
        "    local variables. Before they are used, they must be assigned a value.\n"
        "    A variable that is used before it is assigned a value is assumed to\n"
        "    be defined outside that function; it is known as a 'global'\n"
        "    (or sometimes 'nonlocal') variable. You cannot assign a value to such\n"
        "    a global variable inside a function without first indicating to\n"
        "    Python that this is a global variable, otherwise you will see\n"
        "    an UnboundLocalError.\n"
    )


def unknown(*args):
    _ = current_lang.lang
    return _("    No information is known about this exception.\n")


generic = {
    "IndentationError": indentation_error,
    "NameError": name_error,
    "SyntaxError": syntax_error,
    "TabError": tab_error,
    "UnboundLocalError": unbound_local_error,
    "Unknown": unknown,
}
