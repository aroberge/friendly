"""session.py

Keeps tabs of all settings.
"""
import os.path
import sys

from .my_gettext import current_lang
from . import formatters
from . import friendly_rich
from . import core
from .friendly_exception import FriendlyException


def _write_err(text):
    """Default writer"""
    if session.use_rich:
        session.console.print()
        md = friendly_rich.Markdown(
            text, inline_code_lexer="python", code_theme="brunante"
        )
        if formatters.RICH_HEADER:
            info = session.saved_traceback_info
            if info and "header" in info and info["header"]:
                title = info["header"].replace(":", "")
            else:
                title = "Traceback"
            md = friendly_rich.Panel(md, title=title)
            formatters.RICH_HEADER = False
        session.console.print(md)
    else:
        sys.stderr.write(text)

    if session._debug:
        log_file = os.path.join(os.path.expanduser("~"), "friendly.log")
        with open(log_file, "a", encoding="utf8") as out:
            out.write(text + "\n" + "=" * 70 + "\n\n")


class _State:
    """Keeping track of various parameters in a single object meant
    to be instantiated only once.
    """

    def __init__(self):
        self._captured = []
        self.context = 3
        self.write_err = _write_err
        self.installed = False
        self.running_script = False
        self.saved_traceback_info = None
        self.formatter = formatters.repl
        self._debug = False
        self.console = None
        self.use_rich = False
        self.markdown = False
        self.set_defaults()
        self.set_formatter()

    def set_defaults(self):
        """Sets some defaults for various values"""
        self.include = "explain"
        # self.level = self._default_level = 1
        self.lang = "en"
        self.install_gettext(self.lang)

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
        explanation = self.formatter(self.saved_traceback_info, include=self.include)
        self.write_err(explanation + "\n")

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

    def set_include(self, include):
        if include not in formatters.items_groups:
            raise ValueError(f"{include} is not a valid value.")
        self.include = include

    def get_include(self):
        return self.include

    def set_formatter(self, formatter=None, theme="dark", markdown=False):
        """Sets the default formatter. If no argument is given, the default
        formatter is used.
        """
        self.use_rich = False
        self.markdown = markdown
        if formatter is None or formatter == "repl":
            self.formatter = formatters.repl
        elif formatter == "pre":
            self.formatter = formatters.pre
        elif formatter == "rich":
            self.formatter = formatters.rich_markdown
            self.console = friendly_rich.init_console(theme)
            self.use_rich = True
            self.markdown = True
        elif formatter == "markdown":
            self.formatter = formatters.markdown
            self.markdown = True
        elif formatter == "markdown_docs":
            self.formatter = formatters.markdown_docs
            self.markdown = True
        else:
            self.formatter = formatter

    def quote(self, text):
        """Surrounds text by single quote, or by backquote if formatter
        is markdown type.
        """
        if self.markdown:
            return f"`{text}`"
        else:
            return f"'{text}'"

    def install(self, lang=None, redirect=None, include="explain"):
        """Replaces sys.excepthook by friendly_traceback's own version."""
        _ = current_lang.translate

        if lang is not None:
            self.install_gettext(lang)
        if redirect is not None:
            self.set_redirect(redirect=redirect)
        if include != self.include:
            self.set_include(include)

        sys.excepthook = self.exception_hook
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

    def explain_traceback(self, redirect=None):
        """Replaces a standard traceback by a friendlier one, giving more
        information about a given exception than a standard traceback.
        Note that this excludes SystemExit and KeyboardInterrupt which
        are re-raised.

        By default, the output goes to sys.stderr or to some other stream
        set to be the default by another API call.  However, if
           redirect = some_stream
        is specified, the output goes to that stream, but without changing
        the global settings.
        """
        _ = current_lang.translate
        etype, value, tb = sys.exc_info()
        if etype is None:
            print(_("Nothing to show: no exception recorded."))
            return
        self.exception_hook(etype, value, tb, redirect=redirect)

    def exception_hook(self, etype, value, tb, redirect=None):
        """Replaces a standard traceback by a friendlier one,
        except for SystemExit and KeyboardInterrupt which
        are re-raised.

        The values of the required arguments are typically the following:

            etype, value, tb = sys.exc_info()

        By default, the output goes to sys.stderr or to some other stream
        set to be the default by another API call.  However, if
           redirect = some_stream
        is specified, the output goes to that stream for this call,
        but the session settings is restored afterwards.
        """

        if etype.__name__ == "SystemExit":
            raise SystemExit(str(value))
        elif etype.__name__ == "KeyboardInterrupt":
            raise KeyboardInterrupt(str(value))
        elif issubclass(etype, FriendlyException):  # Internal errors
            self.write_err(str(value))
            return

        if redirect is not None:
            saved_current_redirect = self.write_err
            self.set_redirect(redirect=redirect)

        try:
            self.saved_traceback_info = info = core.get_traceback_info(
                etype, value, tb, self._debug
            )
            explanation = self.formatter(info, include=self.include)
        except FriendlyException as e:
            self.write_err(e)
            return

        self.write_err(explanation)
        # Ensures that we start on a new line; essential for the console
        if not explanation.endswith("\n"):
            self.write_err("\n")

        if redirect is not None:
            self.set_redirect(redirect=saved_current_redirect)


session = _State()
