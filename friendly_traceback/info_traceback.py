"""info_traceback.py

First version - needs to be documented.
"""
import inspect
import os
import traceback

from . import info_generic
from . import info_specific
from . import utils
from .my_gettext import current_lang
from .info_variables import get_var_info

from .source_cache import cache, highlight_source
from .path_info import is_excluded_file


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

    # normal Python traceback
    python_tb = traceback.format_exception(etype, value, tb)
    # change formatting to conform to our line break notation
    # Note, some lines in python_tb have embedded \n as well as ending \n
    # we do not want to remove the embedded ones.

    temp = []
    for item in python_tb:
        temp.append(item.rstrip())
    info["python_traceback"] = python_tb = temp

    if hasattr(value, "friendly"):  # for custom exceptions
        friendly = getattr(value, "friendly")
    else:
        friendly = []

    # Note: the numbered comments refer to the example above
    set_header(info, friendly)  # [1]
    info["message"] = get_message(etype.__name__, value)  # [1a]
    set_generic(info, friendly, etype, value)  # [2]
    set_cause(info, friendly, etype, value)  # [3]

    # Get all calls made
    records = inspect.getinnerframes(tb, cache.context)
    # Do not show traceback from our own code
    records = []
    for record in inspect.getinnerframes(tb, cache.context):
        frame, filename, linenumber, _func, lines, index = record
        if is_excluded_file(filename):
            continue
        else:
            records.append(record)

    simulated_python_tb = format_simulated_python_traceback(records, etype, value)

    str_python_tb = "\n".join(python_tb)
    str_simulated_python_tb = "\n".join(simulated_python_tb)
    simulated_no_heading = "\n".join(simulated_python_tb[1:])

    if str_simulated_python_tb == str_python_tb:
        info["simulated_python_traceback"] = simulated_python_tb
    elif simulated_no_heading == str_python_tb:
        # For syntax error in the standard Python console, often there is
        # no title line "Traceback (most recent call last):"
        info["simulated_python_traceback"] = simulated_python_tb[1:]
    else:
        info["simulated_python_traceback"] = simulated_python_tb
        info["simulated_python_traceback"][0] = "Simulated " + simulated_python_tb[0]

    if issubclass(etype, SyntaxError):
        return info

    if not records:
        return info

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
    filename = cache.get_true_filename(filename)
    if name == "last_call":
        get_header = last_call_header
    else:
        get_header = exception_raised_header
    info["%s_header" % name] = get_header(linenumber, filename)  # [4]
    info["%s_source" % name] = source_info["source"]  # [5]

    if "line" in source_info and source_info["line"] is not None:
        var_info = get_var_info(source_info["line"], frame)
        if var_info:
            info["%s_variables" % name] = var_info  # [6]


def cannot_analyze_string():
    _ = current_lang.translate
    return _(
        "Unfortunately, no additional information is available:\n"
        "the content of file '<string>' is not accessible.\n"
    )


def set_header(info, friendly):
    """Sets the header for the exception"""
    _ = current_lang.translate
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
    _ = current_lang.translate
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
    if filename in cache.cache:
        source, line = cache._get_partial_source(filename, linenumber, None)
    elif filename == "<string>":  # note: it might have been cached with this name
        source = cannot_analyze_string()
        lines = source.split("\n")
        new_lines = []
        for _line in lines:
            new_lines.append("    " + _line)
        source = "\n".join(new_lines)
        line = None
    elif filename and os.path.abspath(filename):
        source, line = highlight_source(linenumber, index, lines)
        if not source:
            print("Problem: source of %s is not available" % filename)
    elif not filename:
        raise FileNotFoundError("Cannot find %s" % filename)

    if not source.endswith("\n"):
        source += "\n"

    return {"source": source, "line": line}


def last_call_header(linenumber, filename):
    _ = current_lang.translate
    return _("Execution stopped on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def exception_raised_header(linenumber, filename):
    _ = current_lang.translate
    return _("Exception raised on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def process_parsing_error(etype, value, info):
    _ = current_lang.translate
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    partial_source, _ignore = cache._get_partial_source(filepath, linenumber, offset)

    info["parsing_error"] = _(
        "Python could not parse the file '{filename}'\n"
        "beyond the location indicated below by --> and ^.\n"
    ).format(filename=utils.shorten_path(filepath))

    info["parsing_error_source"] = f"{partial_source}\n"


def format_simulated_python_traceback(records, etype, value):
    result = ["Traceback (most recent call last):"]

    for record in records:
        frame, filename, linenumber, _func, lines, index = record
        source_info = get_partial_source(filename, linenumber, lines, index)
        badline = source_info["line"]
        if badline is None:
            badline = ""
        result.append(
            '  File "{}", line {}, in {}\n    {}'.format(
                filename, linenumber, _func, badline.strip()
            )
        )

    if issubclass(etype, SyntaxError):
        filename = value.filename
        linenumber = value.lineno
        offset = value.offset
        msg = value.msg
        lines = cache.get_source(filename)
        result.append('  File "{}", line {}'.format(filename, linenumber))
        try:
            _line = lines[linenumber - 1].rstrip()
            badline = _line.strip()
            offset = offset - (len(_line) - len(badline))  # removing indent
            result.append("    {}".format(badline))
            result.append(" " * (3 + offset) + "^")
        except Exception:
            pass
        result.append("{}: {}".format(etype.__name__, msg))
        return result

    try:
        valuestr = str(value)
    except Exception:
        valuestr = "unknown"

    result.append("%s: %s" % (etype.__name__, valuestr))
    return result
