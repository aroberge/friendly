"""Experimental module to automatically install Friendly-traceback
as a replacement for the standard traceback in IDLE."""

import sys

from idlelib import rpc
from idlelib import run

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    set_formatter,
    start_console,
)
from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import helpers  # noqa
from friendly_traceback import source_cache

__all__ = list(helpers.keys())
__all__.append("set_formatter")


def install_in_idle_shell():
    exclude_file_from_traceback(run.__file__)
    rpchandler = rpc.objecttable["exec"].rpchandler  # noqa

    def get_lines(filename, linenumber):
        lines = rpchandler.remotecall("linecache", "getlines", (filename, None), {})
        new_lines = []
        for line in lines:
            if not line.endswith("\n"):
                line += "\n"
            if filename.startswith("<pyshell#") and line.startswith("    "):
                # Remove extra indentation added in the shell
                line = line[4:]
            new_lines.append(line)
        if linenumber is None:
            return new_lines
        return new_lines[linenumber - 1 : linenumber]

    source_cache.idle_get_lines = get_lines

    install(include="friendly_tb")
    set_formatter("repl")
    print("Friendly-traceback installed.")


if sys.version_info >= (3, 10):
    install_in_idle_shell()
else:
    print("Friendly-traceback cannot be installed in this version of IDLE.")
    print("Using Friendly's own console instead")
    start_console()
