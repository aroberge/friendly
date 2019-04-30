"""formatter.py

First version - needs to be documented.
"""
import inspect
import os
import runpy

from . import generic_info
from . import specific_info
from . import utils
from .my_gettext import current_lang
from .friendly_var_info import get_var_info

CONTEXT = utils.CONTEXT
CONSOLE_SOURCE = utils.CONSOLE_SOURCE

# ====================
# The following is an example of a formatted traceback, with each
# part identified by a number enclosed by brackets
# corresponding to a comment in the function get_traceback_info

# [1]
# Python exception:
#     UnboundLocalError: local variable 'a' referenced before assignment

# [2]
# In Python, variables that are used inside a function are known as
# local variables. Before they are used, they must be assigned a value.
# A variable that is used before it is assigned a value is assumed to
# be defined outside that function; it is known as a 'global'
# (or sometimes 'nonlocal') variable. You cannot assign a value to such
# a global variable inside a function without first indicating to
# Python that this is a global variable, otherwise you will see
# an UnboundLocalError.

# [3]
# Likely cause:
#     The variable that appears to cause the problem is 'a'.
#     Try inserting the statement
#         global a
#     as the first line inside your function.
#
# [4]
# Execution stopped on line 14 of file 'C:\Users...\test_unbound_local_error.py'.

# [5]
#    12:
#    13:     try:
# -->14:         inner()
#    15:     except Exception:

# [6]
# inner: <function test_unbound_local_error.<loca... >

# [7]
# Exception raised on line 11 of file 'C:\Users\...\test_unbound_local_error.py'.

# [8]
#     9:     def inner():
#    10:         b = 2
# -->11:         a = a + b
#    12:

# [9]
# b: 2


def get_traceback_info(etype, value, tb, running_script=False):
    """ Gathers the basic information related to a traceback and
    returns the result in a dict.
    """
    info = {}
    # Note: the numbered comments refer to the example above
    info["header"] = get_header(etype.__name__, value)  # [1]
    info["generic"] = get_generic_explanation(etype.__name__, etype, value)  # [2]

    if issubclass(etype, SyntaxError) and value.filename == "<string>":
        cause = cannot_analyze_string()
    else:
        cause = get_likely_cause(etype, value)

    if cause is not None:
        info["cause"] = cause  # [3]

    if issubclass(etype, SyntaxError):
        return info

    # Get all calls made
    records = inspect.getinnerframes(tb, CONTEXT)

    # Last call made
    if running_script:
        # Do not show traceback from our own code
        excluded_files = excluded_file_names()
        for record in records[:-1]:
            _frame, filename, linenumber, _func, lines, index = record
            if filename in excluded_files:
                continue
            break
    else:
        _frame, filename, linenumber, _func, lines, index = records[0]

    info["last_call header"] = last_call_header(linenumber, filename)  # [4]
    source_info = get_partial_source(filename, linenumber, lines, index)
    info["last_call source"] = source_info["source"]  # [5]

    if "line" in source_info and source_info["line"] is not None:
        result = get_var_info(source_info["line"], _frame)
        if result:
            info["last_call variables"] = result  # [6]

    # Origin of the exception
    if len(records) > 1:
        _frame, filename, linenumber, _func, lines, index = records[-1]
        # [7] below
        info["exception_raised header"] = exception_raised_header(linenumber, filename)
        source_info = get_partial_source(filename, linenumber, lines, index)
        info["exception_raised source"] = source_info["source"]  # [8]

        if "line" in source_info and source_info["line"] is not None:
            result = get_var_info(source_info["line"], _frame)
            if result:
                info["exception_raised variables"] = result  # [9]

    return info


def cannot_analyze_string():
    _ = current_lang.lang
    return _(
        "        Unfortunately, no additional information is available:\n"
        "        the content of file '<string>' is not accessible.\n"
    )


def excluded_file_names():
    """In many places, by default we exclude the files from this project,
       as well as runpy from the standard Python library, in order to
       restrict tracebacks to code written by the users.
    """
    excluded = [runpy.__file__]
    dirname = os.path.dirname(__file__)
    for file in os.listdir(os.path.dirname(__file__)):
        excluded.append(os.path.join(dirname, file))
    return excluded


def get_header(name, value):
    """Provides the header for a standard Python exception"""
    _ = current_lang.lang
    # fmt: off
    return _(
        "    Python exception: \n"
        "        {name}: {value}\n"
    ).format(name=name, value=value)
    # fmt: on


def get_generic_explanation(name, etype, value):
    """Provides a generic explanation about a particular exception.
    """
    if name in generic_info.generic:
        explanation = generic_info.generic[name](etype, value)
    else:
        explanation = generic_info.generic["Unknown"]()
    return explanation


def get_likely_cause(etype, value):
    """Gets the likely cause of a given exception based on some information
       specific to a given exception.
    """
    _ = current_lang.lang
    if etype.__name__ in specific_info.get_cause:
        cause = specific_info.get_cause[etype.__name__](etype, value)
        if cause is not None:
            if issubclass(etype, SyntaxError):
                return cause
            else:
                return _("    Likely cause:\n{cause}").format(cause=cause)
    return None


def get_partial_source(filename, linenumber, lines, index):
    """Gets the part of the source where an exception occurred,
       formatted in a pre-determined way, as well as the content
       of the specific line where the exception occurred.
    """
    if filename == "<string>":
        source = cannot_analyze_string()
        line = None
    elif filename in CONSOLE_SOURCE:
        _filename, source = CONSOLE_SOURCE[filename]
        source, line = utils.get_partial_source(filename, linenumber, None)
    elif filename and os.path.abspath(filename):
        filename = os.path.basename(filename)
        source, line = utils.highlight_source(linenumber, index, lines)
    elif not filename:
        raise FileNotFoundError("Cannot find %s" % filename)

    return {"source": source, "line": line}


def last_call_header(linenumber, filename):
    _ = current_lang.lang
    return _(
        "    Execution stopped on line {linenumber} of file '{filename}'.\n"
    ).format(linenumber=linenumber, filename=filename)


def exception_raised_header(linenumber, filename):
    _ = current_lang.lang
    return _(
        "    Exception raised on line {linenumber} of file '{filename}'.\n"
    ).format(linenumber=linenumber, filename=filename)
