"""core.py

The exception hook at the heart of Friendly-traceback.

You should not need to use any of the functions defined here;
they are considered to be internal functions, subject to change at any
time. If functions defined in __init__.py do not meet your needs,
please file an issue.

IMPORTANT: All the traceback information is collected in a dict called 'info'
which is passed around as an argument to many functions where its content
can be changed. Admittedly, this is going against the "best practices"
from modern functional programming where only immutable objects are
passed to functions which do not produce side effects.

I have found that passing this 'info' object around was an easier way
to figure out when a change is made as one can simply do a string search
and locate a particular message, instead of attempting to follow
function call after function call.
"""
import inspect
from itertools import dropwhile
import os
import re
import traceback

from . import info_generic
from . import info_specific
from . import info_variables
from . import utils

from .my_gettext import current_lang

from .source_cache import cache, highlight_source
from .path_info import is_excluded_file, EXCLUDED_FILE_PATH

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
#
# inner: <function test_unbound_local_error.<loca... >

# [5]
# Exception raised on line 11 of file 'C:\Users\...\test_unbound_local_error.py'.
#     9:     def inner():
#    10:         b = 2
# -->11:         a = a + b
#
# [6]
# b: 2


def get_traceback_info(etype, value, tb, debug=False):
    """Gathers the basic information related to a traceback and
    returns the result in a dict.
    """
    _ = current_lang.translate

    if etype is None or not hasattr(etype, "__name__"):
        print("Invalid arguments passed to exception hook.")
        return

    # Note: the numbered comments refer to the example above
    info = {"header": _("Python exception:")}  # [1]
    info["message"] = get_message(etype.__name__, value)  # [1a]
    info["generic"] = info_generic.get_generic_explanation(etype.__name__)  # [2]

    # Unlike what we just did, in many function calls below,
    # we pass the dict info as an argument and add to its content.
    # This is the opposite of what is done in functional programming
    # and is a deliberate choice we made.

    records = get_records(tb, cache)
    python_tb = traceback.format_exception(etype, value, tb)
    format_python_tracebacks(records, etype, value, python_tb, info)

    if issubclass(etype, SyntaxError):
        return process_syntax_error(etype, value, info, debug)

    if not records:
        info["WARNING"] = "WARNING: no records found."
        return info

    format_python_tracebacks(records, etype, value, python_tb, info)

    if len(records) > 1:
        frame, filename, linenumber, _func, lines, index = records[0]
        set_call_info(
            info, "last_call", filename, linenumber, lines, index, frame
        )  # [4]

    frame, filename, linenumber, _func, lines, index = records[-1]
    set_call_info(
        info, "exception_raised", filename, linenumber, lines, index, frame
    )  # [5]

    try:
        info_specific.get_likely_cause(etype, value, info, frame)  # [3]
    except Exception:
        info["WARNING"] = "WARNING: Internal error caught in `get_likely_cause()`."
        if debug:
            raise
    return info


def process_syntax_error(etype, value, info, debug):
    """Completes the information that can be obtained for a syntax error
    and its subclasses.
    """
    from .syntax_errors import analyze_syntax

    if value.filename == "<string>":  # Temporary cause
        info["cause"] = cannot_analyze_string()
        return info
    elif value.filename == "<stdin>":
        info["cause"] = cannot_analyze_stdin()
        return info
    elif value.filename == "<fstring>":
        info["cause"] = cannot_analyze_fstring()
        return info

    try:
        analyze_syntax.set_cause_syntax(etype, value, info)  # [3]
    except Exception:
        info["WARNING"] = "WARNING: Internal error caught in `process_syntax_error()`."
        if debug:
            raise
    return info


def get_records(tb, cache):
    """Get the traceback frrame history, excluding those originating
    from our own code included either at the beginning or at the
    end of the traceback.
    """
    records = inspect.getinnerframes(tb, cache.context)
    records = list(dropwhile(lambda record: is_excluded_file(record.filename), records))
    records.reverse()
    records = list(dropwhile(lambda record: is_excluded_file(record.filename), records))
    records.reverse()
    return records


def format_python_tracebacks(records, etype, value, python_tb, info):
    """When required, a standard Python traceback might be required to be
    included as part of the information shown to the user.
    This function does the required formatting.

    This function defines 3 traceback:
    1. The standard Python traceback, given by Python
    2. A "simulated" Python traceback, which is essentially the same as
       the one given by Python, except that it excludes modules from this
       project.  In addition, for RecursionError, this traceback is often
       further shortened, compared with a normal Python traceback.
    3. A potentially shortened traceback, which does not include too much
       output so as not to overwhelm beginners. It also include information
       about the code on any line mentioned.
    """
    _ = current_lang.translate
    suppressed = ["\n       ... " + _("More lines not shown.") + " ...\n"]

    python_tb = [line.rstrip() for line in python_tb]

    tb = create_traceback(records, etype, value, info)
    if len(tb) > 9:
        shortened_tb = tb[0:2] + suppressed + tb[-5:]
    else:
        shortened_tb = tb[:]

    pattern = re.compile(r'File "(.*)", ')
    temp = []
    for line in shortened_tb:
        match = re.search(pattern, line)
        if match:
            line = line.replace(match.group(1), utils.shorten_path(match.group(1)))
        temp.append(line)
    shortened_tb = temp

    header = "Traceback (most recent call last):"  # not included in records
    if python_tb[0].startswith(header):
        tb.insert(0, header)
        shortened_tb.insert(0, header)

    if "RecursionError" in python_tb[-1]:
        tb = []
        exclude = False
        for line in python_tb:  # excluding our own code
            if exclude and line.strip() == "exec(code, self.locals)":
                continue
            exclude = False
            for filename in EXCLUDED_FILE_PATH:
                if filename in line:
                    exclude = True
                    break
            if exclude:
                continue
            tb.append(line)
        if len(tb) > 12:
            tb = tb[0:4] + suppressed + tb[-5:]

    info["simulated_python_traceback"] = "\n".join(tb) + "\n"
    info["shortened_traceback"] = "\n".join(shortened_tb) + "\n"
    info["original_python_traceback"] = "\n".join(python_tb) + "\n"
    return


def create_traceback(records, etype, value, info):
    """Using records that exclude code from certain files,
    creates a list from which a standard-looking traceback can
    be created.
    """
    result = []

    for record in records:
        frame, filename, linenumber, _func, lines, index = record
        source_info = get_partial_source(filename, linenumber, lines, index)
        result.append('  File "{}", line {}, in {}'.format(filename, linenumber, _func))
        bad_line = source_info["line"]
        if bad_line is not None:
            result.append("    {}".format(bad_line.strip()))

        info["bad_line"] = bad_line or " "
        info["filename"] = filename or " "
        info["linenumber"] = linenumber or None

    if issubclass(etype, SyntaxError):
        info["filename"] = filename = value.filename
        info["linenumber"] = linenumber = value.lineno
        offset = value.offset
        msg = value.msg
        lines = cache.get_source_lines(filename)
        result.append('  File "{}", line {}'.format(filename, linenumber))
        try:
            _line = lines[linenumber - 1].rstrip()
            bad_line = _line.strip()
            offset = offset - (len(_line) - len(bad_line))  # removing indent
            result.append("    {}".format(bad_line))
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


def get_message(name, value):
    """Provides the message for a standard Python exception"""
    if hasattr(value, "msg"):
        return f"{name}: {value.msg}\n"
    return f"{name}: {value}\n"


def get_partial_source(filename, linenumber, lines, index):
    """Gets the part of the source where an exception occurred,
    formatted in a pre-determined way, as well as the content
    of the specific line where the exception occurred.
    """
    _ = current_lang.translate

    if filename in cache.cache:
        source, line = cache.get_formatted_partial_source(filename, linenumber, None)
    elif (
        filename == "<string>"
    ):  # note: Something might have been cached with this name
        source = cannot_analyze_string()
        line = None
    elif filename and os.path.abspath(filename):
        source, line = highlight_source(linenumber, index, lines)
        if not source:
            line = "1"
            if filename == "<stdin>":
                source = _(
                    "        To see the lines of code that cause the problem, \n"
                    "        you must use the Friendly Console and not a \n"
                    "        regular Python console.\n"
                )
            else:
                source = _("Problem: source of '{filename}' is not available\n").format(
                    filename=filename
                )
    elif not filename:
        raise FileNotFoundError("Cannot find %s" % filename)

    if not source.endswith("\n"):
        source += "\n"

    return {"source": source, "line": line}


def cannot_analyze_stdin():
    """Typical case: friendly_traceback is imported in an ordinary Python
    interpreter (REPL), and the user does not activate the friendly
    console.
    """
    _ = current_lang.translate
    return _(
        "Unfortunately, no additional information is available:\n"
        "the content of file '<stdin>' is not accessible.\n"
        "Are you using a regular Python console instead of a Friendly-console?\n"
    )


def cannot_analyze_string():
    """Typical case: some code is executed using exec(), and the 'filename'
    is set to <string>.
    """
    _ = current_lang.translate
    return _(
        "Unfortunately, no additional information is available:\n"
        "the content of file '<string>' is not accessible.\n"
    )


def cannot_analyze_fstring():
    """Typical case: an f-string contains some code with syntax error."""
    _ = current_lang.translate
    return _(
        "You used an f-string that contains invalid Python code.\n"
        "Unfortunately, no additional information is available:\n"
        "the content of file '<fstring>' is not accessible.\n"
    )


def set_call_info(info, header_name, filename, linenumber, lines, index, frame):
    """This will output something like the following:

    [4]
    Execution stopped on line 14 of file 'C:...test_unbound_local_error.py'.
       12:
       13:     try:
    -->14:         inner()

    inner: <function test_unbound_local_error.<loca... >

    [5]
    Exception raised on line 11 of file 'C:...test_unbound_local_error.py'.
        9:     def inner():
       10:         b = 2
    -->11:         a = a + b

    [6]
    b = 2
    """
    _ = current_lang.translate
    source_info = get_partial_source(filename, linenumber, lines, index)
    info["%s_header" % header_name] = get_location_header(  # [4] or [5]
        linenumber, filename, header_name
    )
    info["%s_source" % header_name] = source_info["source"]

    var_info = info_variables.get_var_info(source_info["source"], frame)
    if var_info:
        info["%s_variables_header" % header_name] = _("Known objects shown above:")
        info["%s_variables" % header_name] = var_info  # [6]


def get_location_header(linenumber, filename, header_name=None):
    from .config import session

    _ = current_lang.translate
    filename = utils.shorten_path(filename)
    if session.use_rich:
        filename = f"`'{filename}'`"

    if header_name == "exception_raised":
        return _("Exception raised on line {linenumber} of file {filename}.\n").format(
            linenumber=linenumber, filename=filename
        )
    else:
        return _("Execution stopped on line {linenumber} of file {filename}.\n").format(
            linenumber=linenumber, filename=filename
        )
