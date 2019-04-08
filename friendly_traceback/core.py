"""install.py

Just a first draft as proof of concept.
"""

import gettext
import inspect
import os
import sys

from .generic_info import generic
from .specific_info import get_cause


__all__ = ["install", "get_output", "explain"]


def _write_err(text):
    """Default writer"""
    sys.stderr.write(text)


def highlight_source(linenumber, index, lines):
    """Displays a few relevant lines from a file, showing line numbers
       and identifying a particular line.
    """
    new_lines = []
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits
    i = linenumber - index
    for line in lines:
        if i == linenumber:
            num = with_mark.format(i)
        else:
            num = no_mark.format(i)
        new_lines.append(num + line.rstrip())
        i += 1
    return "\n".join(new_lines)


def python_exception_info(filename, linenumber, partial_source):
    return _(
        "\n"
        "    Error found in file '{filename}' on line {linenumber}.\n\n"
        "{partial_source}\n"
    ).format(filename=filename, linenumber=linenumber, partial_source=partial_source)


class _State:
    """Keeping track of various parameters in a single object meant
       to be instantiated only once.
    """

    def __init__(self):
        self._captured = []
        self.redirect = None
        self.context = 3
        self.write_err = _write_err
        self.install_gettext("en")

    def explain(self, etype, value, tb, redirect=None):
        """Replaces a standard traceback by a friendlier one"""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect

        name = etype.__name__
        self.give_generic_explanation(name, value)

        records = inspect.getinnerframes(tb, self.context)
        self.give_likely_cause(name, etype, value)

        last_call = records[0]
        if len(records) > 1:
            origin = records[-1]
        else:
            origin = None

        _frame, filename, linenumber, _func, lines, index = last_call
        info = self.get_source_info(filename, linenumber, lines, index)
        self.show_source_info(info)

        if origin is not None:
            _frame, filename, linenumber, _func, lines, index = origin
            info = self.get_source_info(filename, linenumber, lines, index)
            self.show_source_info(info, last_call=False)

    def get_source_info(self, filename, linenumber, lines, index):
        if filename and os.path.abspath(filename):
            filename = os.path.basename(filename)
        elif not filename:
            return None
        if index is not None:
            source = highlight_source(linenumber, index, lines)
        else:
            return None

        return {"filename": filename, "source": source, "linenumber": linenumber}

    def show_source_info(self, info, last_call=True):

        if last_call:
            message = _(
                "\n"
                "    Execution stopped in file '{filename}' on line {linenumber}.\n"
                "\n"
                "{source}\n"
            ).format(**info)

        else:
            message = _(
                "\n"
                "    Exception raised in file '{filename}' on line {linenumber}.\n"
                "\n"
                "{source}\n"
            ).format(**info)

        self.write_err(message)

    def give_generic_explanation(self, name, value):
        """Provides a generic explanation about a particular
           error.
        """
        if name in generic:
            explanation = generic[name]()
        else:
            explanation = generic["Unknown"]()
        self.write_err(
            _(
                "\n"
                "    Python exception: \n"
                "        {name}: {value}\n\n"
                "{explanation}"
            ).format(name=name, value=value, explanation=explanation)
        )

    def give_likely_cause(self, name, etype, value):
        if name in get_cause:
            explanation = get_cause[name](etype, value)
        else:
            return
        self.write_err(
            _("\n" "    Likely cause: \n" "{explanation}").format(
                name=name, value=value, explanation=explanation
            )
        )

    def get_captured(self, flush=True):
        """Returns the result of captured output as a string"""
        result = "".join(self._captured)
        if flush:
            self._captured.clear()
        return result

    def capture(self, txt):
        """Captures the output instead of writing to stderr."""
        self._captured.append(txt)

    def install_gettext(self, lang):
        """Sets the current language for gettext."""
        gettext_lang = gettext.translation(
            lang,
            localedir=os.path.normpath(
                os.path.join(os.path.dirname(__file__), "locales")
            ),
            languages=[lang],
            fallback=True,
        )
        gettext_lang.install()

    def write_err(self, text):
        """Writes to stderr. Can be overriden."""
        sys.stderr.write(text)

    def install(self, lang=None, redirect=None):
        """
        Replaces sys.excepthook by friendly_traceback's own version
        """
        sys.excepthook = self.explain
        if lang is not None:
            self.install_gettext(lang)
        if self.redirect == "capture":
            self.write_err == self.capture
        elif self.redirect is not None:
            self.write_err = self.redirect


state = _State()

# ----------------
# Public API
# ----------------


def install(lang=None, redirect=None):
    """
    Replaces sys.excepthook by friendly_traceback's own version
    """
    state.install(lang=lang, redirect=redirect)


def explain(etype, value, tb, redirect=None):
    """Replaces a standard traceback by a friendlier one"""
    state.explain(etype, value, tb, redirect=redirect)


def get_output(flush=True):
    """Returns the result of captured output as a string which can be
       written anywhere desired.

       By default, flushes all the captured content.
       However, this can be overriden if desired.
    """
    return state.get_captured(flush=flush)
