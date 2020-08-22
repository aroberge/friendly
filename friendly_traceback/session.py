"""session.py

Keeps tabs of all settings.
"""
import sys

from .my_gettext import current_lang
from . import formatters
from . import friendly_rich


def _write_err(text):
    """Default writer"""
    if session.use_rich:
        md = friendly_rich.Markdown(text)
        friendly_rich.console.print(md)
    else:
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
        self.saved_traceback_info = None
        self.formatter = formatters.pre
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

    def show_traceback_info_again(self):
        """If has not been cleared, write the traceback info again, using
           the default stream.

           This is intended to be used when a user changes the verbosity
           level and wishes to see a traceback reexplained without having
           to execute the code again.
        """
        _ = current_lang.translate
        if self.saved_traceback_info is None:
            print(_("Nothing to show: no exception recorded."))
            return
        explanation = self.formatter(self.saved_traceback_info, level=self.level)
        self.write_err(explanation + "\n")

    def print_itemized_traceback(self):
        """This is a helper function for developer who want to write a formatter.
           It prints each item recorded in a traceback dict.
        """
        if self.saved_traceback_info is None:
            print("No traceback has been recorded.")
            return

        print("Printing each item of traceback info dict.\n")
        for item in self.saved_traceback_info:
            print("-" * 50)
            print("item = ", item)
            print(self.saved_traceback_info[item])
            print()

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

    def set_verbosity(self, verbosity=None):
        """Sets the "verbosity level".

           If no argument is given, the default value is set.

           If a value of 0 is chosen, Frendly-traceback is uninstalled
           and sys.__excepthook__ is reset to its previous value.
           """
        # verbosity is the public name replacing level, which was used previously
        # For simplicity, we still use level here.
        _ = current_lang.translate
        if verbosity is None:
            self.level = self._default_level
            return
        elif verbosity not in range(0, 10):
            self.write_err(
                _("Verbosity level {level} not valid.").format(level=verbosity)
            )
            return

        self.level = verbosity

    def set_formatter(self, formatter=None):
        """Sets the default formatter. If no argument is given, the default
           formatter is used.
        """
        if formatter is None or formatter == "pre":
            self.formatter = formatters.pre
        elif formatter == "rich":
            self.formatter = formatters.rich_markdown
        elif formatter == "markdown":
            self.formatter = formatters.markdown
        elif formatter == "markdown_docs":
            self.formatter = formatters.markdown_docs
        else:
            self.formatter = formatter

    def install(self, lang=None, redirect=None, verbosity=None):
        """Replaces sys.excepthook by friendly_traceback's own version.
        """
        _ = current_lang.translate

        if lang is not None:
            self.install_gettext(lang)
        if redirect is not None:
            self.set_redirect(redirect=redirect)
        if verbosity is not None:
            self.set_verbosity(verbosity)

        sys.excepthook = self.except_hook
        self.installed = True

    def uninstall(self):
        """Resets sys.excepthook to the Python default"""
        self.installed = False
        sys.excepthook = sys.__excepthook__

    def set_redirect(self, redirect=None):
        """Sets where the output is redirected."""
        if redirect == "capture":
            self.write_err = self.capture
        elif redirect is not None:
            self.write_err = redirect
        else:
            self.write_err = _write_err


session = _State()

# This settings is intentionally made here to give it visibility
session.use_rich = False  # can be over-ridden elsewhere
