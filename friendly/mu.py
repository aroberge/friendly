import sys

from .my_gettext import current_lang  # noqa
from .runtime_errors import name_error

if "InteractiveShell" in repr(sys.excepthook):
    from .ipython import *  # noqa  Will automatically install
    from .ipython import __all__
    from friendly import set_formatter
    import colorama

    colorama.deinit()
    colorama.init(convert=False, strip=False)

    def day():
        """Day theme for Mu's REPL"""
        set_formatter(
            "light", color_system="truecolor", force_jupyter=False, background="#FEFEF7"
        )

    def night():
        """Night theme for Mu's REPL"""
        set_formatter(
            "dark", color_system="truecolor", force_jupyter=False, background="#373737"
        )

    def ft():
        """ft = Friendly Theme Mu's REPL (high contrast).
        This uses the standard colours for Friendly with dark consoles.
        """
        set_formatter(
            "dark", color_system="truecolor", force_jupyter=False, background="#000000"
        )

    def bw():
        """Black and White theme for Mu's REPL.
        This is similar to Mu's high contrast theme."""
        set_formatter(
            "bw", color_system="truecolor", force_jupyter=False, background="#000000"
        )

    Friendly.bw = bw  # noqa
    Friendly.ft = ft  # noqa
    Friendly.day = day  # noqa
    Friendly.night = night  # noqa

    day()
    __all__.append("bw")
    __all__.append("ft")
    __all__.append("day")
    __all__.append("night")

else:
    from friendly.console_helpers import *  # noqa
    from friendly.console_helpers import helpers  # noqa
    from friendly import run  # noqa

    def _cause():
        _ = current_lang.translate
        return _("Friendly themes are only available in Mu's REPL.\n")

    name_error.CUSTOM_NAMES = {}
    for name in ("bw", "day", "ft", "night"):
        name_error.CUSTOM_NAMES[name] = _cause

    __all__ = list(helpers.keys())
    __all__.append("run")

try:
    __all__.remove("dark")
    __all__.remove("light")
except ValueError:
    pass
