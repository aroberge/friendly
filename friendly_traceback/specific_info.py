"""specific_info.py

Attempts to provide some specific information about the cause
of a given exception.
"""
import os


from . import utils
from .my_gettext import current_lang
from .analyze_syntax import find_likely_cause


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


def name_error(etype, value):
    _ = current_lang.lang
    # value is expected to be something like
    #
    # NameError: name 'c' is not defined
    #
    # By splitting value using ', we can extract the variable name.
    return _("        In your program, the unknown name is '{var_name}'.\n").format(
        var_name=str(value).split("'")[1]
    )


def syntax_error(etype, value):
    _ = current_lang.lang
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    # message = value.msg
    partial_source = utils.get_partial_source(filepath, linenumber, offset)
    filename = os.path.basename(filepath)
    info = _(
        "        Python could not parse the file '{filename}'\n"
        "        beyond the location indicated below by --> and ^.\n"
        "\n"
        "{source}\n"
    ).format(filename=filename, source=partial_source)

    source = utils.get_source(filepath)
    cause = find_likely_cause(source, linenumber, offset)
    print("CAUSE = ", cause)
    this_case = syntax_error_causes(cause)

    return info + this_case


def tab_error(etype, value):
    _ = current_lang.lang
    filename = value.filename
    linenumber = value.lineno
    offset = value.offset
    source = utils.get_partial_source(filename, linenumber, offset)
    filename = os.path.basename(filename)
    return _(
        "        Python could not parse the file '{filename}'\n"
        "        beyond the location indicated below by --> and ^.\n"
        "\n"
        "{source}\n"
    ).format(filename=filename, source=source)


def unbound_local_error(etype, value):
    _ = current_lang.lang
    # value is expected to be something like
    #
    # UnboundLocalError: local variable 'a' referenced before assignment
    #
    # By splitting value using ', we can extract the variable name.
    return _(
        "        The variable that appears to cause the problem is '{var_name}'.\n"
        "        Try inserting the statement\n"
        "            global {var_name}\n"
        "        as the first line inside your function."
    ).format(var_name=str(value).split("'")[1])


def zero_division_error(*args):
    return None


get_cause = {
    "IndentationError": indentation_error,
    "NameError": name_error,
    "SyntaxError": syntax_error,
    "TabError": tab_error,
    "UnboundLocalError": unbound_local_error,
    "ZeroDivisionError": zero_division_error,
}


def syntax_error_causes(cause):
    _ = current_lang.lang

    if cause == "Assigning to Python keyword":
        return _(
            "        My best guess: you were trying to assign a value\n"
            "        to a Python keyword. This is not allowed.\n"
            "\n"
        )

    if cause == "class missing colon":
        return _(
            "       My best guess: you wanted to define a class but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "def missing colon":
        return _(
            "       My best guess: you wanted to define a function but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "elif missing colon":
        return _(
            "       My best guess: you wrote an elif statement but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "else missing colon":
        return _(
            "       My best guess: you wrote an else statement but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "finally missing colon":
        return _(
            "       My best guess: you wrote a finally statement but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "for missing colon":
        return _(
            "       My best guess: you wrote a for loop but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "if missing colon":
        return _(
            "       My best guess: you wrote an if statement but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    if cause == "while missing colon":
        return _(
            "       My best guess: you wrote a while loop but\n"
            "       forgot to add a colon ':' at the end\n"
            "\n"
        )

    return _(
        "        Currently, we cannot give you more information\n"
        "        about the likely cause of this error.\n"
        "\n"
    )
