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
from friendly_traceback.formatters import select_items, repl_indentation, no_result

__all__ = list(helpers.keys())
__all__.append("set_include")


def idle_writer(output, color=None):
    """Use this instead of standard sys.stderr to write traceback so that
    they can be colorized.
    """
    if isinstance(output, str):
        if color is None:
            sys.stdout.shell.write(output, "stderr")  # noqa
        else:
            sys.stdout.shell.write(output, color)  # noqa
        return
    for fragment in output:
        if isinstance(fragment, str):
            sys.stdout.shell.write(fragment, "stderr")  # noqa
        elif len(fragment) == 2:
            sys.stdout.shell.write(fragment[0], fragment[1])  # noqa
        else:
            sys.stdout.shell.write(fragment[0], "stderr")  # noqa


def format_traceback(text):
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("    "):
            new_lines.append((line, "default"))
        elif line:
            new_lines.append((line, "stderr"))
        new_lines.append(("\n", "default"))
    return new_lines


def idle_formatter(info, include="friendly_tb"):
    """Formatter that takes care of color definitions.
    """
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = ["\n"]
    for item in items_to_show:
        if item == "header":
            continue

        if "header" in item:
            color = "stderr"
        elif "source" in item:
            color = "default"
        else:
            color = "stdout"

        if item in info:
            if "traceback" in item:
                result.extend(format_traceback(info[item]))
            else:
                indentation = spacing[repl_indentation[item]]
                for line in info[item].split("\n"):
                    result.append((indentation + line + "\n", color))

    if result == ["\n"]:
        return no_result(info, include)

    return result


def install_in_idle_shell():
    exclude_file_from_traceback(run.__file__)
    rpchandler = rpc.objecttable["exec"].rpchandler  # noqa

    def get_lines(filename, linenumber):
        lines = rpchandler.remotecall("linecache", "getlines", (filename, None), {})
        new_lines = []
        for line in lines:
            if not line.endswith("\n"):
                line += "\n"
            if filename.startswith("<pyshell#") and line.startswith("\t"):
                # Remove extra indentation added in the shell (\t == 8 spaces)
                line = "    " + line[1:]
            new_lines.append(line)
        if linenumber is None:
            return new_lines
        return new_lines[linenumber - 1 : linenumber]

    source_cache.idle_get_lines = get_lines

    set_formatter(idle_formatter)
    install(include="friendly_tb", redirect=idle_writer)
    idle_writer("Friendly-traceback installed.\n", "stdout")
    # Current limitation
    idle_writer("               WARNING\n", "hit")  # noqa
    idle_writer(
        "Friendly-traceback cannot handle SyntaxErrors for code entered in the shell.\n"
    )


if sys.version_info >= (3, 10):
    install_in_idle_shell()
    sys.stderr = sys.stdout.shell  # noqa
else:
    sys.stderr.write(
        "Friendly-traceback cannot be installed in this version of IDLE.\n"
    )
    sys.stderr.write("Using Friendly's own console instead.\n")
    start_console()
