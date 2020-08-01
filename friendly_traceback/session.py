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
        self._default_except_hook = None
        self.installed = False
        self.running_script = False
        self.traceback_info = None
        self.set_defaults()

    def set_defaults(self):
        """Sets some defaults for various values"""
        self.level = self._default_level = 1
        self.lang = "en"
        self.install_gettext(self.lang)

    def set_exception_hook(self, hook=None, _default=None):
        """Sets the custom exception hook to be used."""
        if _default is not None:  # sets by core.py
            self._default_except_hook = _default
            self.except_hook = _default
        elif hook is not None:  # user defined
            self.except_hook = hook
        else:  # used to reset
            self.except_hook = self._default_except_hook

    def clear_traceback(self):
        """Removes previous traceback_info"""
        self.traceback_info = None

    def show_traceback_info_again(self):
        """If has not been cleared, write the traceback info again, using
           the default stream.

           This is intended to be used when a user changes the verbosity
           level and wishes to see a traceback reexplained without having
           to execute the code again.
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

    def set_level(self, level=None, verbosity=None):
        """Sets the "verbosity level" and possibly resets sys.__excepthook__"""
        _ = current_lang.translate
        if verbosity is not None:
            level = verbosity
        elif level is None:
            level = self._default_level

        if level == 0:
            self.uninstall()
            return

        if level == self.level:
            return

        if (
            self.formatter == formatters.format_traceback
            and abs(level) in formatters.choose_formatter
        ):
            self.level = level
        else:
            self.write_err(
                _("Level {level} not available; using default.").format(level=level)
            )
            self.level = self._default_level

    set_verbosity = set_level

    def set_formatter(self, formatter=None):
        """Sets the default formatter. If no argument is given, the default
           formatter, based on the value for the level, is used.
        """
        if formatter is None:
            self.formatter = formatters.format_traceback
        else:
            self.formatter = formatter

    def install(self, lang=None, redirect=None, level=None):
        """Replaces sys.excepthook by friendly_traceback's own version."""
        if level is None:
            if not self.installed:
                level = 1
            else:
                level = self.level
        self.installed = True

        if lang is not None:
            self.install_gettext(lang)
        self.set_redirect(redirect=redirect)
        self.set_level(level=level)
        sys.excepthook = self.except_hook

    def uninstall(self):
        """Resets sys.excepthook to the Python default"""
        self.installed = False
        sys.excepthook = sys.__excepthook__
        self.level = 0

    def set_redirect(self, redirect=None):
        """Sets where the output is redirected."""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err


session = _State()
