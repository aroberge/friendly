"""core.py

The exception hook at the heart of Friendly-traceback
"""

import inspect
import os
import sys
import traceback

from . import info_generic
from . import info_specific
from . import utils
from .my_gettext import current_lang
from .session import session
from .info_variables import get_var_info

from .source_cache import cache, highlight_source
from .path_info import is_excluded_file
from .friendly_exception import FriendlyException


# The following is the function called `explain` in public_api.py


def explain_traceback(redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
       information about a given exception than a standard traceback.
       Note that this excludes SystemExit and KeyboardInterrupt which
       are re-raised.

       By default, the output goes to sys.stderr or to some other stream
       set to be the default by another API call.  However, if
          redirect = some_stream
       is specified, the output goes to that stream, but without changing
       the global settings.

       If the string "capture" is given as the value for redirect, the
       output is saved and can be later retrieved by get_output().
    """
    # get_output() refers to a function in the public API

    etype, value, tb = sys.exc_info()
    exception_hook(etype, value, tb, redirect=redirect)


def exception_hook(etype, value, tb, redirect=None):
    """Replaces a standard traceback by a friendlier one,
       except for SystemExit and KeyboardInterrupt which
       are re-raised.

       The values of the required arguments are typically the following:

           etype, value, tb = sys.exc_info()

       By default, the output goes to sys.stderr or to some other stream
       set to be the default by another API call.  However, if
          redirect = some_stream
       is specified, the output goes to that stream for this call,
       but the session settings is restored afterwards.

       If the string "capture" is given as the value for redirect, the
       output is saved and can be later retrieved by get_output().
    """
    # get_output() refers to a function in the public API

    if etype.__name__ == "SystemExit":
        raise SystemExit(str(value))
    if etype.__name__ == "KeyboardInterrupt":
        raise KeyboardInterrupt(str(value))

    if redirect is not None:
        saved_current_redirect = session.write_err
        session.set_redirect(redirect=redirect)

    if session.level == 0:  # Normal Python traceback
        session.write_err("".join(traceback.format_exception(etype, value, tb)))
        if redirect is not None:
            session.set_redirect(redirect=saved_current_redirect)
        return

    try:
        session.traceback_info = info = get_traceback_info(
            etype, value, tb, session.write_err
        )
        explanation = session.formatter(info, level=session.level)
    except FriendlyException as e:
        session.write_err(e)
        return

    session.write_err(explanation)
    # Ensures that we start on a new line; essential for the console
    if not explanation.endswith("\n"):
        session.write_err("\n")

    if redirect is not None:
        session.set_redirect(redirect=saved_current_redirect)


session.set_exception_hook(_default=exception_hook)


def check_syntax(
    *, source=None, filename="Fake filename", path=None, level=None, lang=None
):
    """This uses Python's ``compile()`` builtin which does some analysis of
       the its code argument and will raise an exception if it identifies
       some syntax errors, but also some less common "overflow" and "value"
       errors.

       It can either be used on a file, using the ``path`` argument, or
       on some code passed as a string, using the ``source`` argument.
       For the latter case, one can also specify a corresponding ``filename``:
       this could be useful if this function is invoked from a GUI-based
       editor.

       Note that the ``path`` argument, if provided, takes precedence
       over the ``source`` argument.

       Two additional named arguments, ``level`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.

       Returns a tuple containing a code object and a filename if no exception
       has been raised, False otherwise.

    """
    _ = current_lang.translate

    saved_except_hook, saved_lang, saved_level = _save_settings()
    # saved_lang = _temp_set_lang(lang)

    # if session.installed:
    #     saved_level = session.level
    # else:
    #     saved_level = 0  # normal Python traceback

    if path is not None:
        try:
            with open(path, encoding="utf8") as f:
                source = f.read()
                filename = path
        except Exception:
            # Do not show the Python traceback which would include
            #  the call to open() in the traceback
            if level is None:
                session.set_level(5)
            else:
                session.set_level(level)
            explain_traceback()
            return False
        finally:
            _reset(saved_except_hook, saved_lang, saved_level)

    cache.add(filename, source)
    try:
        code = compile(source, filename, "exec")
    except Exception:
        if level is None:
            session.set_level(1)  # our default
        else:
            session.set_level(level)
        explain_traceback()
        return False
    finally:
        _reset(saved_except_hook, saved_lang, saved_level)

    return code, filename


def run_code(
    *, source=None, filename="Fake filename", path=None, level=None, lang=None
):
    """This uses check_syntax to see if the code is valid and, if so,
       executes it into an empty dict as globals. If no exception is
       raised, this dict is returned. If an exception is raised, False
       is returned.

       It can either be used on a file, using the ``path`` argument, or
       on some code passed as a string, using the ``source`` argument.
       For the latter case, one can also specify a corresponding ``filename``:
       this could be useful if this function is invoked from a GUI-based
       editor.

       Note that the ``path`` argument, if provided, takes precedence
       over the ``source`` argument.

       Two additional named arguments, ``level`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.
    """
    result = check_syntax(
        source=source, filename=filename, path=path, level=level, lang=lang
    )
    if not result:
        return False

    saved_except_hook, saved_lang, saved_level = _save_settings()

    my_globals = {}
    code = result[0]

    try:
        exec(code, my_globals)
    except Exception:
        if level is None:
            session.set_level(1)  # our default
        else:
            session.set_level(level)
        explain_traceback()
        return False
    finally:
        _reset(saved_except_hook, saved_lang, saved_level)

    return my_globals


def _temp_set_lang(lang):
    """If lang is not none, temporarily set session.lang to the provided
       value. Keep track of the original lang setting and return it.

       A value of None for saved_lang indicates that no resetting will
       be required.
       """
    saved_lang = None
    if lang is not None:
        saved_lang = session.get_lang()
        if saved_lang != lang:
            session.set_lang(lang)
        else:
            saved_lang = None
    return saved_lang


def _save_settings():
    current_except_hook = sys.excepthook
    current_lang = session.lang
    current_level = session.level

    return current_except_hook, current_lang, current_level


def _reset(saved_except_hook, saved_lang, saved_level):
    """Resets both level and lang to their original values"""
    if saved_lang is not None:
        session.install_gettext(saved_lang)
    session.set_level(saved_level)
    # set_level(0) restores sys.excepthook to sys.__excepthook__
    # which might not be what is wanted. So, we reset sys.excepthook last
    sys.excepthook = saved_except_hook


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


def get_traceback_info(etype, value, tb, write_err):
    """ Gathers the basic information related to a traceback and
    returns the result in a dict.
    """
    _ = current_lang.translate

    if issubclass(etype, FriendlyException):
        write_err(str(value))
        return {}

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

    # Get all calls made, but remove calls from our code.
    records = inspect.getinnerframes(tb, cache.context)
    records = cleanup_tracebacks(records, write_err)

    info["simulated_python_traceback"] = format_simulated_python_traceback(
        records, etype, value, python_tb
    )

    if issubclass(etype, SyntaxError):
        return info

    if not records:
        info["cause"] = _(
            "        I suspect that you are using a regular\n"
            "        Python console after importing\nFriendly-traceback.\n"
            "        Unfortunately, no further processing can be done.\n"
        )
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


# ============================================================================
# The functions below are ordered alphabetically, ignoring leading underscores
# ============================================================================


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


def cleanup_tracebacks(records, write_err):
    """Remove excluded content from beginning and end of complete tracebacks.

        Tracebacks shown to users should originate in their own code,
        and normally end there as well.  However, in intermediate calls,
        they could possibly invoke some code from files which we had
        decided to exclude.
    """
    if not records:
        return records  # likely an empty list

    for begin, record in enumerate(records):
        frame, filename, linenumber, _func, lines, index = record
        if is_excluded_file(filename):
            continue
        else:
            break

    records.reverse()
    for end, record in enumerate(records):
        frame, filename, linenumber, _func, lines, index = record
        if is_excluded_file(filename):
            continue
        else:
            break

    records.reverse()

    end = len(records) - end
    if end == begin:  # The problem is in our own code!
        # Write in two places to make sure it is noticed!
        write_err("Internal problem with Friendly-traceback!\n")
        print("Internal problem with Friendly-traceback")
        return records

    return records[begin:end]


def exception_raised_header(linenumber, filename):
    _ = current_lang.translate
    return _("Exception raised on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def format_simulated_python_traceback(records, etype, value, python_tb):
    """ When required, a standard Python traceback might be required to be
        included as part of the information shown to the user.
        This function does the required formatting.
    """
    simulated_python_tb = _get_traceback_information(records, etype, value)

    str_python_tb = "\n".join(python_tb)
    str_simulated_python_tb = "\n".join(simulated_python_tb)
    simulated_no_heading = "\n".join(simulated_python_tb[1:])

    if str_simulated_python_tb == str_python_tb:
        result = simulated_python_tb
    elif simulated_no_heading == str_python_tb:
        # For syntax error in the standard Python console, often there is
        # no title line "Traceback (most recent call last):"
        result = simulated_python_tb[1:]
    else:
        result = simulated_python_tb
        result[0] = "Simulated " + simulated_python_tb[0]
    return result


def _get_traceback_information(records, etype, value):
    """ Gets the traceback information in a predefined format.
    """
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


def get_generic_explanation(name, etype, value):
    """Provides a generic explanation about a particular exception.
    """
    if name in info_generic.generic:
        explanation = info_generic.generic[name](etype, value)
    else:
        explanation = info_generic.generic["Unknown"]()
    return explanation


def get_likely_cause(etype, value):
    """Gets the likely cause of a given exception based on some information
       specific to a given exception.
    """
    _ = current_lang.translate
    header, cause = None, None
    if etype.__name__ in info_specific.get_cause:
        cause = info_specific.get_cause[etype.__name__](etype, value)
        if cause is not None:
            message = get_message(etype.__name__, value)
            if etype.__name__ == "SyntaxError" and "invalid syntax" in message:
                header = _("I don't have enough information from Python:")
            else:
                header = _("Likely cause based on the information given by Python:")
    return header, cause


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
        if filename == "<string>":
            # We should no longer see <string> used as a filename;
            # if so, it signals a potential problem we should look into.
            print(
                "Message to developer:",
                " please revise cache to take care of <string> cases.",
            )
        source, line = cache.get_formatted_partial_source(filename, linenumber, None)
    elif (
        filename == "<string>"
    ):  # note: Something might have been cached with this name
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


def last_call_header(linenumber, filename):
    _ = current_lang.translate

    return _("Execution stopped on line {linenumber} of file '{filename}'.\n").format(
        linenumber=linenumber, filename=utils.shorten_path(filename)
    )


def process_parsing_error(etype, value, info):
    _ = current_lang.translate
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    partial_source, _ignore = cache.get_formatted_partial_source(
        filepath, linenumber, offset
    )
    if "-->" in partial_source:
        info["parsing_error"] = _(
            "Python could not understand the code in the file\n"
            "'{filename}'\n"
            "beyond the location indicated below by --> and ^.\n"
        ).format(filename=utils.shorten_path(filepath))
    elif "unexpected EOF while parsing" in repr(value):
        info["parsing_error"] = _(
            "Python could not understand the code the file\n"
            "'{filename}'.\n"
            "It reached the end of the file and expected more content.\n"
        ).format(filename=utils.shorten_path(filepath))
    else:
        info["parsing_error"] = _(
            "Python could not understand the code the file\n"
            "'{filename}'\n"
            "for an unspecified reason.\n"
        ).format(filename=utils.shorten_path(filepath))

    info["parsing_error_source"] = f"{partial_source}\n"


def set_call_info(info, name, filename, linenumber, lines, index, frame):
    """This will outpt something like the following:

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
    source_info = get_partial_source(filename, linenumber, lines, index)
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


def set_cause(info, friendly, etype, value):
    """Sets the cause"""
    if issubclass(etype, SyntaxError) and value.filename == "<string>":
        info["cause"] = cannot_analyze_string()
    elif issubclass(etype, SyntaxError) and value.filename == "<stdin>":
        info["cause"] = cannot_analyze_stdin()
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


def set_generic(info, friendly, etype, value):
    """Sets the value of the generic explanation.

       This might be something like the following:

        In Python, variables that are used inside a function are known as
        local variables. Before they are used, they must be assigned a value.
        A variable that is used before ...
    """
    if "generic" in friendly:
        info["generic"] = friendly["generic"]
    else:
        info["generic"] = get_generic_explanation(etype.__name__, etype, value)


def set_header(info, friendly):
    """Sets the header for the exception"""
    _ = current_lang.translate
    if "header" in friendly:  # [1]
        info["header"] = friendly["header"]
    else:
        info["header"] = _("Python exception:")
