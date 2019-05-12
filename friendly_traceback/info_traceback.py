"""info_traceback.py

First version - needs to be documented.
"""
import inspect
import os
import runpy

from . import info_generic
from . import info_specific
from . import utils
from .my_gettext import current_lang
from .info_variables import get_var_info


# ====================
# The following is an example of a formatted traceback, with each
# part identified by a number enclosed by brackets
# corresponding to a comment in the function get_traceback_info

# [1]
# Python exception:

# [1a]
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
#    12:
#    13:     try:
# -->14:         inner()
#    15:     except Exception:
#
# inner: <function test_unbound_local_error.<loca... >

# [5]
# Exception raised on line 11 of file 'C:\Users\...\test_unbound_local_error.py'.
#     9:     def inner():
#    10:         b = 2
# -->11:         a = a + b
#    12:
#
# b: 2


def get_traceback_info(etype, value, tb):
    """ Gathers the basic information related to a traceback and
    returns the result in a dict.
    """
    info = {}
    if hasattr(value, "friendly"):  # for custom exceptions
        friendly = getattr(value, "friendly")
    else:
        friendly = []

    # Note: the numbered comments refer to the example above
    set_header(info, friendly)  # [1]
    info["message"] = get_message(etype.__name__, value)  # [1a]
    set_generic(info, friendly, etype, value)  # [2]
    set_cause(info, friendly, etype, value)  # [3]

    if issubclass(etype, SyntaxError):
        return info

    # Get all calls made
    records = inspect.getinnerframes(tb, utils.CONTEXT)
    # Do not show traceback from our own code
    new_records = []
    excluded_files = excluded_file_names()
    for record in records:
        frame, filename, linenumber, _func, lines, index = record
        if filename in excluded_files:
            continue
        else:
            new_records.append(record)

    records = new_records
    # Last call made
    frame, filename, linenumber, _func, lines, index = records[0]
    set_call_info(info, "last_call", filename, linenumber, lines, index, frame)  # [4]

    # Origin of the exception
    if len(records) > 1:
        frame, filename, linenumber, _func, lines, index = records[-1]
        set_call_info(
            info, "exception_raised", filename, linenumber, lines, index, frame
        )  # [5]

    return info


def set_call_info(info, name, filename, linenumber, lines, index, frame):
    source_info = get_partial_source(filename, linenumber, lines, index)
    # If the source was cached, the filename we got was not the correct one
    # so we ensure that we have the true filename for the display
    true_filename = source_info["filename"]
    if name == "last_call":
        get_header = last_call_header
    else:
        get_header = exception_raised_header
    info["%s_header" % name] = get_header(linenumber, true_filename)  # [4]
    info["%s_source" % name] = source_info["source"]  # [5]

    if "line" in source_info and source_info["line"] is not None:
        var_info = get_var_info(source_info["line"], frame)
        if var_info:
            info["%s_variables" % name] = var_info  # [6]


def cannot_analyze_string():
    _ = current_lang.lang
    return _(
        "Unfortunately, no additional information is available:\n"
        "the content of file '<string>' is not accessible.\n"
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


def set_header(info, friendly):
    """Sets the header for the exception"""
    _ = current_lang.lang
    if "header" in friendly:  # [1]
        info["header"] = friendly["header"]
    else:
        info["header"] = _("Python exception:")


def get_message(name, value):
    """Provides the message for a standard Python exception"""
    if hasattr(value, "msg"):
        return f"{name}: {value.msg}\n"
    return f"{name}: {value}\n"


def set_generic(info, friendly, etype, value):
    """Sets the value of the generic explanation"""
    if "generic" in friendly:
        info["generic"] = friendly["generic"]
    else:
        info["generic"] = get_generic_explanation(etype.__name__, etype, value)


def get_generic_explanation(name, etype, value):
    """Provides a generic explanation about a particular exception.
    """
    if name in info_generic.generic:
        explanation = info_generic.generic[name](etype, value)
    else:
        explanation = info_generic.generic["Unknown"]()
    return explanation


def set_cause(info, friendly, etype, value):
    """Sets the cause"""
    if issubclass(etype, SyntaxError) and value.filename == "<string>":
        info["cause"] = cannot_analyze_string()
    else:
        if issubclass(etype, SyntaxError):
            process_parsing_error(etype, value, info)
        if "cause" in friendly:
            info["cause"] = friendly["cause"]
            if "cause_header" in friendly:
                info["cause_header"] = friendly["cause_header"]
        else:
            header, cause = get_likely_cause(etype, value)
            if cause is not None:
                info["cause_header"] = header
                info["cause"] = cause


def get_likely_cause(etype, value):
    """Gets the likely cause of a given exception based on some information
       specific to a given exception.
    """
    _ = current_lang.lang
    header, cause = None, None
    if etype.__name__ in info_specific.get_cause:
        cause = info_specific.get_cause[etype.__name__](etype, value)
        if cause is not None:
            if etype.__name__ == "SyntaxError":
                header = _("My best guess:")
            else:
                header = _("Likely cause:")
    return header, cause


def get_partial_source(filename, linenumber, lines, index):
    """Gets the part of the source where an exception occurred,
       formatted in a pre-determined way, as well as the content
       of the specific line where the exception occurred.
    """
    if filename in utils.CACHED_STRING_SOURCES:
        true_name, source = utils.CACHED_STRING_SOURCES[filename]
        source, line = utils.get_partial_source(filename, linenumber, None)
        filename = true_name
    elif filename == "<string>":  # note: it might have been cached with this name
        source = cannot_analyze_string()
        lines = source.split("\n")
        new_lines = []
        for _line in lines:
            new_lines.append("    " + _line)
        source = "\n".join(new_lines)
        line = None
    elif filename and os.path.abspath(filename):
        # filename = os.path.basename(filename)
        source, line = utils.highlight_source(linenumber, index, lines)
    elif not filename:
        raise FileNotFoundError("Cannot find %s" % filename)

    if not source.endswith("\n"):
        source += "\n"

    return {"source": source, "line": line, "filename": filename}


def last_call_header(linenumber, filename):
    _ = current_lang.lang
    return _("Execution stopped on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def exception_raised_header(linenumber, filename):
    _ = current_lang.lang
    return _("Exception raised on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def process_parsing_error(etype, value, info):
    _ = current_lang.lang
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    partial_source, _ignore = utils.get_partial_source(filepath, linenumber, offset)

    info["parsing_error"] = _(
        "Python could not parse the file '{filename}'\n"
        "beyond the location indicated below by --> and ^.\n"
    ).format(filename=utils.shorten_path(filepath))

    info["parsing_error_source"] = f"{partial_source}\n"
