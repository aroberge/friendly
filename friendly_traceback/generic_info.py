"""Basic information about Python exceptions"""
import os
from .my_gettext import current_lang
from . import utils


def arithmetic_error(*args):
    _ = current_lang.lang
    return _(
        "    ArithmeticError is the base class for those built-in exceptions\n"
        "    that are raised for various arithmetic errors.\n"
        "    It is unusual that you are seeing this exception;\n"
        "    normally, a more specific exception should have been raised.\n"
    )


def import_error(*args):
    _ = current_lang.lang
    return _(
        "    This exception indicates that a certain object could not\n"
        "    be imported from a module or package. Most often, this is\n"
        "    because the name of the object is not spelled correctly.\n"
    )


def indentation_error(etype, value):
    _ = current_lang.lang
    filename = value.filename
    linenumber = value.lineno
    offset = value.offset
    source = utils.get_partial_source(filename, linenumber, offset)
    filename = os.path.basename(filename)
    info = _(
        "    Python could not parse the file '{filename}'\n"
        "    beyond the location indicated below by --> and ^.\n"
        "\n"
        "{source}\n"
    ).format(filename=filename, source=source)
    return (
        _(
            "    An IndentationError occurs when a given line of code is\n"
            "    not indented (aligned vertically with other lines) as expected.\n"
        )
        + info
    )


def module_not_found_error(*args):
    _ = current_lang.lang
    return _(
        "    A ModuleNotFoundError exception indicates that you\n"
        "    are trying to import a module that cannot be found by Python.\n"
        "    This could be because you misspelled the name of the module\n"
        "    or because it is not installed on your computer.\n"
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
    return _("    A SyntaxError occurs when Python cannot understand your code.\n")


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


def zero_division_error(*args):
    _ = current_lang.lang
    return _(
        "    A ZeroDivisionError occurs when you are attempting to divide\n"
        "    a value by zero:\n"
        "        result = my_variable / 0\n"
        "    It can also happen if you calculate the remainder of a division\n"
        "    using the modulo operator '%'\n"
        "        result = my_variable % 0"
    )


generic = {
    "ArithmeticError": arithmetic_error,
    "ImportError": import_error,
    "IndentationError": indentation_error,
    "ModuleNotFoundError": module_not_found_error,
    "NameError": name_error,
    "SyntaxError": syntax_error,
    "TabError": tab_error,
    "UnboundLocalError": unbound_local_error,
    "Unknown": unknown,
    "ZeroDivisionError": zero_division_error,
}
