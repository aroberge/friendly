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
    set_lang,
    set_formatter,
)
from friendly_traceback.console import (
    explain,
    friendly_tb,
    more,
    python_tb,
    what,
    where,
    why,
)

from friendly_traceback import friendly_rich

shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)


exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)

install(include="friendly_tb")


__all__ = [
    "explain",
    "friendly_tb",
    "more",
    "python_tb",
    "set_lang",
    "set_formatter",
    "what",
    "where",
    "why",
]

if friendly_rich.rich_available:
    print("Friendly-traceback installed; Rich is available.")
else:
    print("Friendly-traceback installed.")
