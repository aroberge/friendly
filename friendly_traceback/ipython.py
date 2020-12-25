"""Experimental module to automatically install Friendly-traceback
as a replacement for the standard traceback in IPython."""

try:
    from IPython.core import interactiveshell as shell
    from IPython.core import compilerop
except ImportError:
    raise ValueError("IPython cannot be imported.")

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
    set_formatter,
)
from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import helpers  # noqa


__all__ = list(helpers.keys())
__all__.append("set_formatter")

shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)

exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)
install(include="friendly_tb")

set_formatter("repl")
print("Friendly-traceback installed.")
