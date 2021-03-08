import sys

exc_hook_name = repr(sys.excepthook)

if "InteractiveShell" in exc_hook_name:
    from .ipython import *  # noqa  Will automatically install
    from friendly import set_formatter
    import colorama

    colorama.deinit()
    colorama.init(convert=False, strip=False)
    set_formatter("rich", style="light", color_system="truecolor", force_jupyter=False)


else:
    from friendly.console_helpers import *  # noqa
    from friendly.console_helpers import helpers  # noqa
    from friendly import install, run  # noqa

    __all__ = list(helpers.keys())
    __all__.append("install")
    __all__.append("run")


del exc_hook_name
del sys
