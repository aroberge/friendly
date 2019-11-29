"""session.py

Keeps tabs of all settings.
"""

import sys

from .my_gettext import current_lang
from . import formatters


def _write_err(text):
    """Default writer"""
    sys.stderr.write(text)


class _State:
    """Keeping track of various parameters in a single object meant
       to be instantiated only once.
    """

    def __init__(self):
        self.set_formatter()
        self._captured = []
        self.context = 3
        self.write_err = _write_err
        self.except_hook = None
        self.installed = False
        self.lang = "en"
        self.install_gettext(self.lang)
        self.level = 1
        self.set_level(self.level)
        self.running_script = False
        self.traceback_info = None

    def set_exception_hook(self, hook):
        """Sets the custom exception hook to be used."""
        self.except_hook = hook
        self.set_level(self.level)

    def clear_traceback(self):
        """Removes previous traceback_info"""
        self.traceback_info = None

    def show_traceback_info_again(self):
        """If has not been cleared, write the traceback info again, using
           the default stream.

           This is intended to be used when a user changes the verbosity
           level in a GUI.
        """
        if self.traceback_info is None:
            return
        explanation = self.formatter(self.traceback_info, level=self.level)
        self.write_err(explanation)

    def capture(self, txt):
        """Captures the output instead of writing to stderr."""
        self._captured.append(txt)

    def get_captured(self, flush=True):
        """Returns the result of captured output as a string"""
        result = "".join(self._captured)
        if flush:
            self._captured.clear()
        return result

    def install_gettext(self, lang):
        """Sets the current language for gettext."""
        current_lang.install(lang)
        self.lang = lang

    def set_level(self, level):
        """Sets the "verbosity level" and possibly resets sys.__excepthook__"""
        _ = current_lang.translate
        if level == 0:
            sys.excepthook = sys.__excepthook__
            self.level = 0
            return

        if abs(level) in formatters.choose_formatter:
            self.level = level
        else:
            print(_("Level {level} not available; using default.").format(level=level))
        if self.except_hook is not None:
            sys.excepthook = self.except_hook
        self.level = level

    def set_formatter(self, formatter=None):
        """Sets the default formatter. If no argument is given, the default
           formatter, based on the value for the level, is used.
        """
        if formatter is None:
            self.formatter = formatters.format_traceback
        else:
            self.formatter = formatter

    def install(self, lang=None, redirect=None, level=1, hook=None):
        """Replaces sys.excepthook by friendly_traceback's own version."""
        if self.installed:
            return
        self.installed = True

        if lang is not None:
            self.install_gettext(lang)
        self.set_redirect(redirect=redirect)
        self.set_level(level=level)
        if hook is not None:
            self.set_exception_hook(hook)

    def set_redirect(self, redirect=None):
        """Sets where the output is redirected."""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err


session = _State()
