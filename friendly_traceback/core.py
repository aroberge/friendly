"""core.py

Just a first draft as proof of concept.
"""

import locale
import runpy
import sys
import traceback

from .my_gettext import current_lang
from . import formatter


__all__ = ["install", "get_output", "explain"]


def _write_err(text):
    """Default writer"""
    sys.stderr.write(text)


class _State:
    """Keeping track of various parameters in a single object meant
       to be instantiated only once.
    """

    def __init__(self):
        self._captured = []
        self.redirect = None
        self.context = 3
        self.write_err = _write_err
        lang, _ignore = locale.getdefaultlocale()
        self.install_gettext(lang)
        self.level = 0
        self.running_script = False

    def explain(self, etype, value, tb, redirect=None):
        """Replaces a standard traceback by a friendlier one"""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect

        explanation = formatter.explain_traceback(
            etype, value, tb, running_script=self.running_script
        )
        self.write_err(explanation)

        if self.level == 2:
            python_tb = traceback.format_exception(etype, value, tb)
            self.write_err("\n" + "".join(python_tb) + "\n")

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
        current_lang.install(lang)

    def install(self, lang=None, redirect=None):
        """
        Replaces sys.excepthook by friendly_traceback's own version
        """
        sys.excepthook = self.explain

        if lang is not None:
            self.install_gettext(lang)
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = self.redirect

        if redirect is not None:
            self.redirect = redirect


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


def run_script(source):
    state.running_script = True
    mod_dict = runpy.run_module(source, run_name="__main__")
    state.running_script = False
    return mod_dict
