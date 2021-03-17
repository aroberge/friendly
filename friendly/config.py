"""config.py

Keeps tabs of all settings.
"""
import sys

from . import core
from . import debug_helper
from . import formatters
from . import theme
from .my_gettext import current_lang


def _write_err(text):
    """Default writer"""
    if not text.strip():
        return
    if session.use_rich:
        if session.rich_add_vspace:
            session.console.print()
        md = theme.friendly_rich.Markdown(
            text, inline_code_lexer="python", code_theme=theme.CURRENT_THEME
        )
        if formatters.RICH_HEADER:
            title = "Traceback"
            md = theme.friendly_rich.Panel(md, title=title)
            formatters.RICH_HEADER = False
        session.console.print(md)
    else:
        if not text.endswith("\n"):
            text += "\n"
        sys.stderr.write(text)


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
        self.saved_info = []
        self.formatter = formatters.repl
        self.console = None
        self.use_rich = False
        self.rich_add_vspace = True
        self.use_jupyter = False
        self.friendly = []
        self.include = "explain"
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
        if not self.saved_info:
            print(_("Nothing to show: no exception recorded."))
            return
        explanation = self.formatter(self.saved_info[-1], include=self.include)
        self.write_err(explanation)
        # Do not combine with above as 'explanation' could be a list for IDLE
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

    def set_lang(self, lang):
        """Sets the language and, if it is not the current language
        and a traceback exists, the information is recompiled for the
        new target language.
        """
        if lang == self.lang:
            return
        current_lang.install(lang)
        self.lang = lang
        if self.saved_info:
            if not self.friendly:
                debug_helper.log(
                    "Problem: saved_info includes content but friendly doesn't."
                )
            self.friendly[-1].recompile_info()

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

    def set_formatter(
        self, formatter=None, color_system="auto", force_jupyter=None, background=None
    ):
        """Sets the default formatter. If no argument is given, the default
        formatter is used.
        """
        self.use_rich = False
        if formatter is None or formatter == "bw":
            self.formatter = formatters.repl
        elif formatter == "docs":
            self.formatter = formatters.docs
        elif formatter == "jupyter":
            self.formatter = formatters.jupyter
        elif formatter in ["dark", "light"]:
            self.formatter = formatters.rich_markdown
            self.console = theme.init_rich_console(
                style=formatter,
                color_system=color_system,
                force_jupyter=force_jupyter,
                background=background,
            )
            self.use_rich = True
        elif formatter == "markdown":
            self.formatter = formatters.markdown
        elif formatter == "markdown_docs":
            self.formatter = formatters.markdown_docs
        elif isinstance(formatter, str):
            print("Unknown formatter", formatter)
            self.formatter = formatters.repl
        else:
            self.formatter = formatter  # could be provided as a function

    def install(self, lang=None, redirect=None, include="explain"):
        """Replaces sys.excepthook by friendly's own version."""
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

        saved_current_redirect = None
        if redirect is not None:
            saved_current_redirect = self.write_err
            self.set_redirect(redirect=redirect)

        try:
            self.friendly.append(core.FriendlyTraceback(etype, value, tb))
            self.friendly[-1].compile_info()
            info = self.friendly[-1].info
            self.saved_info.append(info)
            explanation = self.formatter(info, include=self.include)
        except Exception as e:
            debug_helper.log("Exception raised in exception_hook().")
            try:
                debug_helper.log(self.friendly[-1].tb_data.filename)
            except Exception:
                pass
            debug_helper.log_error(e)
            return

        self.write_err(explanation)

        # Ensures that we start on a new line; essential for the console
        if hasattr(explanation, "endswith") and not explanation.endswith("\n"):
            self.write_err("\n")

        if saved_current_redirect is not None:
            self.set_redirect(redirect=saved_current_redirect)


session = _State()
