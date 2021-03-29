import sys

exc_hook_name = repr(sys.excepthook)

if "InteractiveShell" in exc_hook_name:
    from .ipython import *  # noqa  Will automatically install
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
        This is like the normal high contrast theme chosen by Mu."""
        set_formatter(
            "bw", color_system="truecolor", force_jupyter=False, background="#000000"
        )

    Friendly.bw = bw  # noqa
    Friendly.ft = ft  # noqa
    Friendly.day = day  # noqa
    Friendly.night = night  # noqa

    day()
    del colorama

else:
    from friendly.console_helpers import *  # noqa
    from friendly.console_helpers import helpers  # noqa
    from friendly import install, run  # noqa

    __all__ = list(helpers.keys())
    __all__.append("install")
    __all__.append("run")


del exc_hook_name
del sys
