import sys

from .my_gettext import current_lang  # noqa
from .runtime_errors import name_error

if "InteractiveShell" in repr(sys.excepthook):
    from .ipython import *  # noqa  # Will automatically install
    from friendly import set_formatter
    from friendly.console_helpers import FriendlyHelpers, helpers
    import colorama

    colorama.deinit()
    colorama.init(convert=False, strip=False)

    def day():
        """Day theme for Mu's REPL"""
        set_formatter(
            "light", color_system="truecolor", force_jupyter=False, background="#FEFEF7"
        )

    def _day_repr():
        _ = current_lang.translate
        return (_("Colour scheme designed Mu's day theme."),)  # noqa

    day.__rich_repr__ = _day_repr

    def night():
        """Night theme for Mu's REPL"""
        set_formatter(
            "dark", color_system="truecolor", force_jupyter=False, background="#373737"
        )

    def _night_repr():
        _ = current_lang.translate
        return (_("Colour scheme designed Mu's night theme."),)  # noqa

    night.__rich_repr__ = _night_repr

    def bw():
        """Black and White theme for Mu's REPL.
        This is similar to Mu's high contrast theme."""
        set_formatter(
            "bw", color_system="truecolor", force_jupyter=False, background="#000000"
        )

    def _bw_repr():
        _ = current_lang.translate
        return (_("Colour scheme designed Mu's high contrast theme."),)  # noqa

    bw.__rich_repr__ = _bw_repr
    Friendly = FriendlyHelpers(["bw", "day", "night"])
    Friendly.bw = bw  # noqa
    Friendly.day = day  # noqa
    Friendly.night = night  # noqa

    day()
    __all__ = list(helpers)
    __all__.append("bw")
    __all__.append("day")
    __all__.append("night")

else:
    from friendly.console_helpers import *  # noqa
    from friendly.console_helpers import FriendlyHelpers, helpers  # noqa
    from friendly import run  # noqa

    Friendly = FriendlyHelpers()

    def _cause():
        _ = current_lang.translate
        return _("Friendly themes are only available in Mu's REPL.\n")

    for name in ("bw", "day", "night"):
        name_error.CUSTOM_NAMES[name] = _cause

    __all__ = list(helpers)
    __all__.append("run")


try:
    __all__.remove("dark")
except ValueError:
    pass
try:
    __all__.remove("light")
except ValueError:
    pass
