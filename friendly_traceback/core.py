"""core.py

Just a first draft as proof of concept.
"""

import configparser
import locale
import os
import runpy
import sys
import traceback

from .my_gettext import current_lang
from . import formatter


def _write_err(text):
    """Default writer"""
    sys.stderr.write(text)


def get_default_lang():
    """The default language to be used for translations is determined
       in order of priority by:
          1. The latest explicit call to Friendly-traceback, either as a flag
             from the command line, or as an argument to a function or method.
          2. The environment value set by the a user in a given console.
             For windows, the value is set with
                set FriendlyLang=some value
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


class _State:
    """Keeping track of various parameters in a single object meant
       to be instantiated only once.
    """

    def __init__(self):
        self._captured = []
        self.redirect = None
        self.context = 3
        self.write_err = _write_err
        lang = get_default_lang()
        self.install_gettext(lang)
        self.level = 0
        self.running_script = False

    def explain(self, etype, value, tb, redirect=None):
        """Replaces a standard traceback by a friendlier one,
           except for SystemExit and KeyboardInterrupt which
           are re-raised.
        """
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err

        if etype.__name__ == "SystemExit":
            raise SystemExit(str(value))
        if etype.__name__ == "KeyboardInterrupt":
            raise KeyboardInterrupt(str(value))

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


def run_script(source):
    state.running_script = True
    mod_dict = runpy.run_module(source, run_name="__main__")
    state.running_script = False
    return mod_dict


# ----------------
# Public API available through a * import
# ----------------

__all__ = ["explain", "get_output", "install", "set_lang"]


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


def install(lang=None, redirect=None):
    """
    Replaces sys.excepthook by friendly_traceback's own version
    """
    state.install(lang=lang, redirect=redirect)


def set_lang(lang):
    """Sets the language to be used by gettext.

       If not translations exist for that language, the original
       English strings will be used.
    """
    state.install_gettext(lang)
