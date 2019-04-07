"""install.py

Just a first draft as proof of concept.
"""

import gettext
import os
import sys

__all__ = ["install", "get_output", "explain"]


class _State:
    """Keeping track of various parameters in a single object meant
       to be instantiated only once.
    """

    def __init__(self):
        self._captured = []

    def explain(self, etype, value, tb, redirect=None):
        global _write_err
        if redirect == "capture":
            _write_err = self.capture
        elif redirect is not None:
            _write_err = redirect

        _write_err(str(etype) + "\n")
        _write_err(str(value) + "\n")
        _write_err(str(tb) + "\n")

    def get_captured(self, flush=True):
        """Returns the result of captured output as a string"""
        result = "".join(self._captured)
        if flush:
            self._captured.clear()
        return result

    def capture(self, txt):
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

    def write_err(self, txt):
        sys.stderr.write(txt)


state = _State()  # noqa


def _write_err(txt):
    sys.stderr.write(txt)


def install():
    """
    Replaces sys.excepthook by friendly_traceback's own version
    """
    sys.excepthook = state.explain


def explain(etype, value, tb, redirect=None):
    state.explain(etype, value, tb, redirect=redirect)


def get_output(flush=True):
    """Returns the result of captured output as a string"""
    return state.get_captured(flush=flush)
