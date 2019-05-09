"""core.py

The central module that controls other aspects of friendly-traceback.
"""

import configparser
import locale
import os
import runpy
import sys
import traceback

from .my_gettext import current_lang
from . import formatters
from . import info_traceback

# ---------------------------------------------
# Note: public API is near the end of this file
# ---------------------------------------------


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
        lang = _get_default_lang()
        self.install_gettext(lang)
        self.level = _get_level()
        self.set_level(self.level)
        self.running_script = False

    def explain(self, etype, value, tb, redirect=None):
        """Replaces a standard traceback by a friendlier one,
           except for SystemExit and KeyboardInterrupt which
           are re-raised.
        """
        self.set_redirect(redirect=redirect)

        if self.level == 0:
            python_tb = traceback.format_exception(etype, value, tb)
            self.write_err("\n" + "".join(python_tb) + "\n")
            return

        if etype.__name__ == "SystemExit":
            raise SystemExit(str(value))
        if etype.__name__ == "KeyboardInterrupt":
            raise KeyboardInterrupt(str(value))

        info = info_traceback.get_traceback_info(etype, value, tb, running_script=False)
        # normal Python traceback
        python_tb = traceback.format_exception(etype, value, tb)
        info["python_traceback"] = "".join(python_tb)
        explanation = self.formatter(info, level=self.level)
        self.write_err(explanation)
        # Ensures that we start on a new line for the console
        if not explanation.endswith("\n"):
            self.write_err("\n")

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

    def set_level(self, level):
        """Sets the "verbosity level" and possibly resets sys.__excepthook__"""
        self.level = level
        if level != 0:
            sys.excepthook = self.explain
        else:
            sys.excepthook = sys.__excepthook__

    def set_formatter(self, formatter=None):
        """Sets the default formatter. If no argument is given, the default
           formatter is used.
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


def run_script(source):
    state.running_script = True
    mod_dict = runpy.run_module(source, run_name="__main__")
    state.running_script = False
    return mod_dict


# ----------------
# Public API available through a * import
# ----------------

__all__ = [
    "explain",
    "get_output",
    "install",
    "set_lang",
    "set_level",
    "get_level",
    "set_formatter",
]


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


def install(redirect=None):
    """
    Replaces sys.excepthook by friendly_traceback's own version
    """
    state.install(redirect=redirect)


def set_formatter(self, formatter=None):
    """Sets the default formatter. If no argument is given, the default
       formatter is used.
    """
    state.set_formatter(formatter=formatter)


def set_lang(lang):
    """Sets the language to be used by gettext.

       If not translations exist for that language, the original
       English strings will be used.
    """
    state.install_gettext(lang)


def set_level(level):
    """Sets the verbosity level to be used.

       0. Normal Python tracebacks - restoring sys.__except_hook
       1. Default
       9. "Default" + Python tracebacks at the end.

       Some other values may be available on an experimental basis.
    """
    state.set_level(level)


def get_level():
    return state.level
