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
import os
import re
import traceback

from itertools import dropwhile

from . import info_generic
from . import info_specific
from . import info_variables
from . import utils

from .my_gettext import current_lang
from .source_cache import cache, highlight_source
from .path_info import is_excluded_file, EXCLUDED_FILE_PATH, path_utils
from .utils import get_significant_tokens
from .syntax_errors import analyze_syntax

try:
    import executing

    executing_available = True
except ImportError:
    executing_available = False


class TracebackData:
    """Raw traceback info obtained from Python.

    Instances of this class are intended to include all the relevant
    information about an exception so that a FriendlyTraceback object
    can be created in any language.

    """

    def __init__(self, etype, value, tb, debug=False):
        """This object is initialized with the standard values for a
        traceback::

            etype, value, tb = sys.exc_info()

        An additional debug parameter can be set to True; this is
        useful during development.
        """
        cache.remove("<fstring>")
        self.exception_type = etype
        self.exception_name = etype.__name__
        self.value = value
        self.message = str(value)
        self.tb = tb
        self.formatted_tb = traceback.format_exception(etype, value, tb)
        self.debug = debug
        self.records = self.get_records(tb)
        self.debug_warning = ""
        self.get_source_info(etype, value)
        self.node_text = ""
        self.node_range = None
        self.original_bad_line = ""
        if not issubclass(etype, SyntaxError) and executing_available:
            self.use_executing()

    def get_records(self, tb):
        """Get the traceback frame history, excluding those originating
        from our own code that are included either at the beginning or
        at the end of the traceback.
        """
        records = inspect.getinnerframes(tb, cache.context)
        records = list(
            dropwhile(lambda record: is_excluded_file(record.filename), records)
        )
        records.reverse()
        records = list(
            dropwhile(lambda record: is_excluded_file(record.filename), records)
        )
        records.reverse()
        # If all the records are removed, it means that all the error
        # is in our own code - or that of the user who chose to exclude
        # some files. If so, we make sure to have something to analyze
        # and help identify the problem.
        if not records and not issubclass(self.exception_type, SyntaxError):
            return inspect.getinnerframes(tb, cache.context)
        return records

    def get_source_info(self, etype, value):
        """Retrieves the file name and the line of code where the exception
        was raised.
        """
        if issubclass(etype, SyntaxError):
            self.filename = value.filename
            if value.text is not None:
                self.bad_line = value.text  # typically includes "\n"
                return
            else:  # this can happen with editors_helpers.check_syntax()
                try:
                    self.bad_line = cache.get_source_lines(value.filename)[
                        value.lineno - 1
                    ]
                except Exception:
                    self.bad_line = "\n"
                return
        elif self.records:
            self.exception_frame, filename, linenumber, _, _, _ = self.records[-1]
            _, line = cache.get_formatted_partial_source(filename, linenumber, None)
            self.filename = filename
            self.bad_line = line.rstrip()
            return

        # We should never reach this stage.
        self.debug_warning += "Internal error in TracebackData.get_source_info."
        self.filename = ""
        self.bad_line = "\n"
        return

    def copy_simulated(self, tb):
        """Gets a copy of the simulated traceback as it is used in at least
        one case to determine the cause.

        Such a case is when we have a circular import.
        """
        self.simulated_python_traceback = tb

    def use_executing(self):
        """If executing is present, try to use it to extract
        potentially useful information about the specific location
        where the exception was raised."""
        self.node_text = ""
        self.node_range = None
        if not self.records:
            return

        tb = self.tb
        while True:
            if tb.tb_frame == self.exception_frame:
                break
            tb = tb.tb_next
            if not tb:
                return

        # TODO: for name error, use tokenize to find out the
        # location of the unknown name

        # The code below does the following:
        #
        # 1) If we can find the node causing the exception as part
        # of the line where the exception is found, we note this location
        # so that we can indicate it later with something like:
        #    20:     b = tuple(range(50))
        #    21:     try:
        # -->22:         print(a[50], b[0])
        #                      ^^^^^
        #    23:     except Exception as e:
        # If the node spans the entire line, we do not bother to indicate
        # its specific location.
        #
        # 2) Sometimes, a node will span multiple lines. For example,
        # line 22 shown above might have been written as:
        #     print(a[
        #            50], b[0])
        #
        # If that is the case, we rewrite the node as a single line.
        #
        # In both cases, we replace our definition (text) of the line that
        # caused the exception by that of the node itself, to be used
        # later for processing.

        try:
            ex = executing.Source.executing(tb)
            self.node_text = ex.text()
            # \n could be a valid newline token or a character within
            # a string; we only want to replace newline tokens.
            if "\n" in self.node_text:
                tokens = get_significant_tokens(self.node_text)
                self.node_text = "".join(tok.string for tok in tokens)
            _bad_line = utils.strip_comment(self.bad_line)
            if (
                self.node_text
                and self.node_text in self.bad_line
                and self.node_text.strip() != _bad_line.strip()
            ):
                begin = self.bad_line.find(self.node_text)
                end = begin + len(self.node_text)
                self.node_range = begin, end
            if self.node_text.strip():
                self.original_bad_line = self.bad_line
                self.bad_line = self.node_text
        except Exception:
            pass


# ====================
# The following is an example of a formatted traceback, with
# some parts identified with (partial) names used below
#
# Python exception:  [header]

# [message]
#     UnboundLocalError: local variable 'a' referenced before assignment

# [generic]
# In Python, variables that are used inside a function are known as
# local variables. Before they are used, they must be assigned a value.
# A variable that is used before it is assigned a value is assumed to
# be defined outside that function; it is known as a 'global'
# (or sometimes 'nonlocal') variable. You cannot assign a value to such
# a global variable inside a function without first indicating to
# Python that this is a global variable, otherwise you will see
# an UnboundLocalError.

# [cause_header and cause]
# Likely cause:
#     The variable that appears to cause the problem is 'a'.
#     Try inserting the statement
#         global a
#     as the first line inside your function.
#

# [last_call_ ...]
# Execution stopped on line 14 of file 'C:\Users...\test_unbound_local_error.py'.
#    12:
#    13:     try:
# -->14:         inner()
#
# inner: <function test_unbound_local_error.<loca... >

# [exception_raised_ ...]
# Exception raised on line 11 of file 'C:\Users\...\test_unbound_local_error.py'.
#     9:     def inner():
#    10:         b = 2
# -->11:         a = a + b
#
# [6]
# b: 2


class FriendlyTraceback:
    """Main class for creating a friendly traceback.

    All the information available to the end user is stored in a
    dict called "info". The various keys of that dict are documented
    in the docstrings of the relevant methods.

    To get all possible attributes set up, one needs to call
    compile_info() after initializing this class. This is done so
    as to allow third-party users to selectively call only one of

    * assign_cause()
    * assign_generic()
    * assign_location()

    if they so wish.

    Various functions are available when using a friendly console,
    which can show part of the information compile here.
    Among those:

    * where() shows the result of assign_location()
    * why() shows the cause, as compiled by assign_cause()
    * hint() is a shorter version of why(), sometimes available.
    * what() shows the information compiled by assign_generic()
    """

    def __init__(self, etype, value, tb, debug=False):
        """The basic argument are those generated after a traceback
        and obtained via::

            etype, value, tb = sys.exc_info()

        The "header" key for the info dict is assigned here."""
        _ = current_lang.translate
        self.tb_data = TracebackData(etype, value, tb, debug)
        self._debug = debug
        self.info = {}
        self.info["debug_warning"] = self.tb_data.debug_warning
        self.info["header"] = _("Python exception:")
        self.assign_message()  # language independent
        self.assign_tracebacks()

    def compile_info(self):
        """Compile all info that was not set in __init__."""
        self.assign_generic()
        self.assign_location()
        self.assign_cause()
        to_remove = []
        for key in self.info:
            if not self.info[key]:
                to_remove.append(key)
        for key in to_remove:
            del self.info[key]

    def recompile_info(self):
        """This is useful if we need to redisplay some information in a
        different language than what was originally used.
        """
        _ = current_lang.translate
        self.info["header"] = _("Python exception:")
        self.assign_tracebacks()
        self.compile_info()

    def assign_cause(self):
        """Determine the cause of an exception, which is what is returned
        by ``why()``.

        Sets the value of the following attributes:

        * cause_header
        * cause

        and possibly:

        * suggest

        the latter being the "hint" appended to the friendly traceback.
        """
        if issubclass(self.tb_data.exception_type, SyntaxError):
            self.set_cause_syntax()
        else:
            self.set_cause_runtime()

    def set_cause_runtime(self):
        """For exceptions other than SyntaxError and subclasses.
        Sets the value of the following attributes:

        * cause_header
        * cause

        and possibly:

        * suggest
        """
        _ = current_lang.translate

        etype = self.tb_data.exception_type
        value = self.tb_data.value
        self._debug = True
        try:
            cause, hint = info_specific.get_likely_cause(
                etype, value, self.exception_frame, self.tb_data
            )  # [3]
            if cause is not None:
                self.info["cause_header"] = _(
                    "Likely cause based on the information given by Python:"
                )
                self.info["cause"] = cause
                if hint:
                    self.info["suggest"] = hint
        except Exception:
            self.info["debug_warning"] = (
                "debug_warning: Internal error caught in"
                " `info.specific.get_likely_cause()`."
            )
            if self._debug:
                raise

    def set_cause_syntax(self):
        """For SyntaxError and subclasses. Sets the value of the following
        attributes:

        * cause_header
        * cause

        and possibly:

        * suggest
        """
        _ = current_lang.translate
        etype = self.tb_data.exception_type
        value = self.tb_data.value
        if self.tb_data.filename in ["<unknown>", "<string>"]:
            return
        try:
            cause, hint = analyze_syntax.set_cause_syntax(etype, value, self.tb_data)
            if cause is not None:
                if "invalid syntax" in self.message:
                    header = _(
                        "Python's error message (invalid syntax) "
                        "cannot be used to identify the problem:"
                    )
                else:
                    header = _("Likely cause based on the information given by Python:")
                self.info["cause_header"] = header
                self.info["cause"] = cause
                if hint:
                    self.info["suggest"] = hint
        except Exception:
            self.info[
                "debug_warning"
            ] = "debug_warning: Internal error caught in `set_cause_syntax()`."
            if value.filename == "<stdin>":
                self.info["cause"] = cannot_analyze_stdin()
            if self._debug:
                raise

    def assign_generic(self):
        """Assigns the generic information about a given error. This is
        the answer to ``what()`` as in "What is a NameError?"

        Sets the value of the following attribute:

        * generic
        """
        self.info["generic"] = info_generic.get_generic_explanation(
            self.tb_data.exception_name
        )

    def assign_location(self):
        """This sets the values of the answers to 'where()', that is
        the information about the location of the exception.

        To determine which attributes will be set, consult the docstring
        of the following methods.

        For SyntaxError and subclasses: self.locate_parsing_error()

        For other types of exceptions, self.locate_exception_raised(),
        and possibly self.locate_last_call().
        """
        if issubclass(self.tb_data.exception_type, SyntaxError):
            self.locate_parsing_error()
            return

        records = self.tb_data.records
        if not records:
            self.info["debug_warning"] += "debug_warning: no records found."
            return
        self.locate_exception_raised(records[-1])
        if len(records) > 1:
            self.locate_last_call(records[0])

    def locate_exception_raised(self, record):
        """Sets the values of the following attributes which are
        part of a friendly-traceback:

        * exception_raised_header
        * exception_raised_source
        * exception_raised_variables
        """
        from .config import session

        _ = current_lang.translate

        frame, filename, linenumber, _func, lines, index = record
        # The following is needed when determining the cause
        self.exception_frame = frame

        source_info = get_partial_source(
            filename, linenumber, lines, index, self.tb_data.node_range
        )
        filename = path_utils.shorten_path(filename)
        if session.use_rich:
            filename = f"`'{filename}'`"

        self.info["exception_raised_header"] = _(
            "Exception raised on line {linenumber} of file {filename}.\n"
        ).format(linenumber=linenumber, filename=filename)
        self.info["exception_raised_source"] = source_info["source"]

        if self.tb_data.node_text:
            line = self.tb_data.node_text
        else:
            line = source_info["line"]

        var_info = info_variables.get_var_info(line, frame)
        if var_info:
            self.info["exception_raised_variables"] = var_info

    def locate_last_call(self, record):
        """Sets the values of the following attributes:

        * last_call_header
        * exception_raised_source
        * last_call_variables
        """
        from .config import session

        _ = current_lang.translate

        frame, filename, linenumber, _func, lines, index = record
        source_info = get_partial_source(filename, linenumber, lines, index)
        filename = path_utils.shorten_path(filename)
        if session.use_rich:
            filename = f"`'{filename}'`"

        self.info["last_call_header"] = _(
            "Execution stopped on line {linenumber} of file {filename}.\n"
        ).format(linenumber=linenumber, filename=filename)
        self.info["last_call_source"] = source_info["source"]

        var_info = info_variables.get_var_info(source_info["line"], frame)
        if var_info:
            self.info["last_call_variables"] = var_info

    def locate_parsing_error(self):
        """Sets the values of the attributes:

        * parsing_error
        * parsing_source_error
        """
        _ = current_lang.translate
        value = self.tb_data.value
        filepath = value.filename
        if filepath in ["<unknown>", "<string>"]:
            self.info["parsing_error"] = _(
                "`{filename}` is not a regular Python file whose contents\n"
                "can be analyzed.\n"
            ).format(filename=filepath)
            return
        partial_source, _ignore = cache.get_formatted_partial_source(
            filepath, value.lineno, value.offset
        )
        if "-->" in partial_source:
            self.info["parsing_error"] = _(
                "Python could not understand the code in the file\n"
                "'{filename}'\n"
                "beyond the location indicated by --> and ^.\n"
            ).format(filename=path_utils.shorten_path(filepath))
        elif "unexpected EOF while parsing" in repr(value):
            self.info["parsing_error"] = _(
                "Python could not understand the code the file\n"
                "'{filename}'.\n"
                "It reached the end of the file and expected more content.\n"
            ).format(filename=path_utils.shorten_path(filepath))
        else:
            self.info["parsing_error"] = _(
                "Python could not understand the code in the file\n"
                "'{filename}'\n"
                "for an unspecified reason.\n"
            ).format(filename=path_utils.shorten_path(filepath))

        self.info["parsing_error_source"] = f"{partial_source}\n"

    def assign_message(self):
        """Assigns the error message, as the attribute ``message``
        which is something like::

            NameError: name 'a' is not defined
        """
        exc_name = self.tb_data.exception_name
        value = self.tb_data.value
        if hasattr(value, "msg"):
            self.info["message"] = f"{exc_name}: {value.msg}\n"
        else:
            self.info["message"] = f"{exc_name}: {value}\n"
        self.message = self.info["message"]

    def assign_tracebacks(self):
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

        These are given by the attributes:

        * original_python_traceback
        * simulated_python_traceback
        * shortened_traceback
        """
        _ = current_lang.translate
        if not hasattr(self, "message"):
            self.assign_message()
        suppressed = ["\n       ... " + _("More lines not shown.") + " ...\n"]

        python_tb = [line.rstrip() for line in self.tb_data.formatted_tb]

        tb = self.create_traceback()
        if len(tb) > 10:
            shortened_tb = tb[0:2] + suppressed + tb[-6:]
        else:
            shortened_tb = tb[:]

        pattern = re.compile(r'File "(.*)", ')
        temp = []
        for line in shortened_tb:
            match = re.search(pattern, line)
            if match:
                line = line.replace(
                    match.group(1), path_utils.shorten_path(match.group(1))
                )
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

        self.info["simulated_python_traceback"] = "\n".join(tb) + "\n"
        self.info["shortened_traceback"] = "\n".join(shortened_tb) + "\n"
        self.info["original_python_traceback"] = "\n".join(python_tb) + "\n"
        # The following is needed for some determining the cause in at
        # least one case.
        self.tb_data.copy_simulated("\n".join(tb) + "\n")

    def create_traceback(self):
        """Using records that exclude code from certain files,
        creates a list from which a standard-looking traceback can
        be created.
        """
        result = []
        for record in self.tb_data.records:
            frame, filename, linenumber, _func, lines, index = record
            source_info = get_partial_source(filename, linenumber, lines, index)
            result.append(
                '  File "{}", line {}, in {}'.format(filename, linenumber, _func)
            )
            bad_line = source_info["line"]
            if bad_line is not None:
                result.append("    {}".format(bad_line.strip()))

        if issubclass(self.tb_data.exception_type, SyntaxError):
            value = self.tb_data.value
            offset = value.offset
            filename = value.filename
            lines = cache.get_source_lines(filename)
            result.append('  File "{}", line {}'.format(filename, value.lineno))
            _line = value.text
            if _line is None:
                try:
                    _line = lines[value.lineno - 1]
                except Exception:
                    pass
            if _line is not None:
                if filename == "<fstring>" and lines == ["\n"]:
                    # Before Python 3.9, the traceback included a fake
                    # file for f-strings which only included parts of
                    # the f-string content.
                    cache.add(filename, _line)
                _line = _line.rstrip()
                bad_line = _line.strip()
                if bad_line:
                    offset = offset - (len(_line) - len(bad_line))  # removing indent
                    result.append("    {}".format(bad_line))
                    result.append(" " * (3 + offset) + "^")
        result.append(self.info["message"].strip())
        return result


def get_partial_source(filename, linenumber, lines, index, text_range=None):
    """Gets the part of the source where an exception occurred,
    formatted in a pre-determined way, as well as the content
    of the specific line where the exception occurred.
    """
    _ = current_lang.translate

    if filename in cache.cache:
        source, line = cache.get_formatted_partial_source(
            filename, linenumber, offset=None, text_range=text_range
        )
    elif filename and os.path.abspath(filename):
        source, line = highlight_source(
            linenumber, index, lines, offset=None, text_range=text_range
        )
        if not source:
            line = ""
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
