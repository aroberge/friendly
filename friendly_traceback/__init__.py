# note that public_api.py limits the number of names imported via __all__

import sys as _sys
import warnings as _warnings

_valid_version = _sys.version_info.major >= 3 and _sys.version_info.minor >= 6

if not _valid_version:
    print("Python 3.6 or newer is required.")
    _sys.exit()


# Ensure that warnings are not shown to the end user, as they could
# cause confusion.  Eventually, we might want to interpret them like
# we do for Exceptions.
_warnings.simplefilter("ignore")

del _valid_version
del _sys
del _warnings

from .version import __version__  # noqa
from .public_api import *  # noqa


def start_console(
    local_vars=None,
    use_rich=False,
    include="friendly_tb",
    lang="en",
    banner=None,
    theme="dark",
):
    """Starts a Friendly console"""
    from . import console

    console.start_console(
        local_vars=local_vars,
        use_rich=use_rich,
        include=include,
        lang=lang,
        banner=banner,
        theme=theme,
    )
