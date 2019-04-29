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
CONSOLE_NAME = utils.CONSOLE_NAME


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


def explain_traceback(etype, value, tb, running_script=False):
    """ Provides a basic explanation for a traceback.

        Rather than a standard explanation, we provide an example with
        four different parts, which are noted as such in the code.

        # 1. Generic explanation
        Python exception:
            NameError: name 'c' is not defined

        A NameError exception indicates that a variable or
        function name is not known to Python.
        Most often, this is because there is a spelling mistake.
        However, sometimes it is because the name is used
        before being defined or given a value.

        # 2. Likely cause
        Likely cause:
            In your program, the unknown name is 'c'.

        # 3. last call made
        Execution stopped on line 48 of file 'tb_common.py'.

           46:                     mod = __import__(name)
           47:                     if function is not None:
        -->48:                         getattr(mod, function)()
           49:                 except Exception:

        # 4. origin of the exception (could be the same as 3.)
        Exception raised  on line 8 of file 'raise_name_error.py'.

            6:     # Should raise NameError
            7:     a = 1
        --> 8:     b = c
            9:     d = 3

    """
    result = []

    # 1. Generic explanation
    result.append(provide_generic_explanation(etype.__name__, etype, value))
    if issubclass(etype, SyntaxError) and value.filename == "<string>":
        cause = cannot_analyze_string()
    else:
        cause = get_likely_cause(etype, value)

    # 2. Likely cause
    if cause is not None:
        result.append(cause)

    if issubclass(etype, SyntaxError):
        return "\n".join(result)

    # first, get all calls made
    records = inspect.getinnerframes(tb, CONTEXT)

    # 3. Last call made
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

    if filename == "<string>":
        info = cannot_analyze_string()
    else:
        info = get_source_info(filename, linenumber, lines, index)
    result.append(add_source_info(info))

    if "line" in info:
        res = get_var_info(info["line"], _frame)
        if res:
            result.extend(res)

    # 4. origin of the exception
    if len(records) > 1:
        _frame, filename, linenumber, _func, lines, index = records[-1]
        if filename == "<string>":
            info = cannot_analyze_string()
        else:
            info = get_source_info(filename, linenumber, lines, index)
        result.append(add_source_info(info, last_call=False))
        if "line" in info:
            get_var_info(info["line"], _frame)
        if res:
            result.extend(res)

    return "\n".join(result)


def provide_generic_explanation(name, etype, value):
    """Provides a generic explanation about a particular error.
    """
    _ = current_lang.lang
    if name in generic_info.generic:
        explanation = generic_info.generic[name](etype, value)
    else:
        explanation = generic_info.generic["Unknown"]()
    # fmt: off
    return _(
        "\n"
        "    Python exception: \n"
        "        {name}: {value}\n"
        "\n"
        "{explanation}"
    ).format(name=name, value=value, explanation=explanation)
    # fmt: on


def get_likely_cause(etype, value):
    _ = current_lang.lang
    if etype.__name__ in specific_info.get_cause:
        cause = specific_info.get_cause[etype.__name__](etype, value)
        if cause is not None:
            if issubclass(etype, SyntaxError):
                return cause
            else:
                return _("    Likely cause:\n{cause}").format(cause=cause)
    return None


def get_source_info(filename, linenumber, lines, index):
    _ = current_lang.lang

    if filename in CONSOLE_SOURCE:
        _filename, source = CONSOLE_SOURCE[filename]
        source, line = utils.get_partial_source(filename, linenumber, None)
    elif filename and os.path.abspath(filename):
        filename = os.path.basename(filename)
        source, line = utils.highlight_source(linenumber, index, lines)
    elif not filename:
        raise FileNotFoundError("Cannot find %s" % filename)

    return {
        "filename": filename,
        "source": source,
        "linenumber": linenumber,
        "line": line,
    }


def add_source_info(info, last_call=True):
    _ = current_lang.lang
    if last_call:
        message = _(
            "\n"
            "    Execution stopped on line {linenumber} of file '{filename}'.\n"
            "\n"
            "{source}\n"
        ).format(**info)

    else:
        message = _(
            "\n"
            "    Exception raised on line {linenumber} of file '{filename}'.\n"
            "\n"
            "{source}\n"
        ).format(**info)

    return message
