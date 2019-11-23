"""session.py

Keeps tabs of all settings.
"""

import configparser
import locale
import os
import sys

from .my_gettext import current_lang
from . import formatters


def _write_err(text):
    """Default writer"""
    sys.stderr.write(text)


def _get_default_lang():
    """Determines the default language to be used for translations.

    The default language to be used for translations is determined
    in order of priority by:
        1. The latest explicit call to Friendly-traceback, either as a flag
           from the command line, or as an argument to a function or method.
        2. The environment value set by the a user in a given console.
           For windows, the value is set with ``set FriendlyLang=some_value``
           and is stored in all uppercase
        3. A value set in a .ini file in the user's home directory.
        4. A value determined by the locale - e.g. default language for the OS
    """
    lang, _ignore = locale.getdefaultlocale()  # lowest priority

    loc = os.path.join(os.path.expanduser("~"), "friendly.ini")
    if os.path.isfile(loc):
        config = configparser.ConfigParser()
        config.read(loc)
        if "friendly" in config:
            if "lang" in config["friendly"]:
                lang = config["friendly"]["lang"]

    if "FRIENDLYLANG" in os.environ:
        lang = os.environ["FRIENDLYLANG"]

    return lang


def _get_level():
    """Determines the default verbosity level.

    The verbosity level to be used by Friendly-traceback is determined
    in order of priority by:
        1. The latest **explicit** call to Friendly-traceback as a flag
           from the command line, or by a call to the set_level() function.
        2. The environment value set by the a user in a given console.
           For windows, the value is set with ``set FriendlyLevel=some_value``
           and is stored in all uppercase.
        3. A value set in a .ini file in the user's home directory.
        4. A default value of 1
    """
    level = 1

    loc = os.path.join(os.path.expanduser("~"), "friendly.ini")
    if os.path.isfile(loc):
        config = configparser.ConfigParser()
        config.read(loc)
        if "friendly" in config:
            if "level" in config["friendly"]:
                level = config["friendly"]["level"]

    if "FRIENDLYLEVEL" in os.environ:
        level = os.environ["FRIENDLYLEVEL"]

    return level


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
        self.lang = _get_default_lang()
        self.install_gettext(self.lang)
        self.level = _get_level()
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

    def install(self, lang=None, redirect=None, level=1):
        """Replaces sys.excepthook by friendly_traceback's own version."""
        if lang is not None:
            self.install_gettext(lang)
        self.set_redirect(redirect=redirect)
        self.set_level(level=level)

    def set_redirect(self, redirect=None):
        """Sets where the output is redirected."""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err


state = _State()
