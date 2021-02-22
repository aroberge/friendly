"""Experimental module to automatically install Friendly-traceback
as a replacement for the standard traceback in IDLE."""

import inspect
from pathlib import Path
import sys  # noqa

from idlelib import rpc
from idlelib import run as idlelib_run

from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import helpers  # noqa
from friendly_traceback import source_cache
from friendly_traceback.formatters import select_items, repl_indentation, no_result
from friendly_traceback.my_gettext import current_lang


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
    """We format tracebacks using the default stderr color (usually read)
    except that lines with code are shown in the default color (usually black).
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("    "):
            new_lines.append((line, "default"))
        elif line:
            new_lines.append((line, "stderr"))
        new_lines.append(("\n", "default"))
    return new_lines


def format_source(text, keep_caret):
    """Formats the source code.

    Often, the location of an error is indicated by one or more ^ below
    the line with the error. IDLE uses highlighting with red background the
    normal single character location of an error.
    This function replaces the ^ used to highlight an error by the same
    highlighting scheme used by IDLE.
    """
    lines = text.split("\n")
    caret_set = {"^"}
    error_line = -2
    begin = end = 0
    for index, line in enumerate(lines):
        if set(line.strip()) == caret_set:
            error_line = index
            begin = line.find("^")
            end = begin + len(line.strip())
            break

    new_lines = []
    for index, line in enumerate(lines):
        if index == error_line and not keep_caret:
            continue
        elif index == error_line - 1:
            new_lines.append((line[0:begin], "default"))
            new_lines.append((line[begin:end], "ERROR"))
            new_lines.append((line[end:], "default"))
        else:
            new_lines.append((line, "default"))
        new_lines.append(("\n", "default"))
    return new_lines


def format_text(info, item, indentation):
    """Format text with embedded code fragment surrounded by backquote characters."""
    new_lines = []
    for line in info[item].split("\n"):
        if "`" in line and line.count("`") % 2 == 0:
            fragments = line.split("`")
            for index, fragment in enumerate(fragments):
                if index == 0:
                    new_lines.append((indentation + fragment, "stdout"))
                elif index % 2:
                    if "Error" in fragment:
                        new_lines.append((fragment, "stderr"))
                    else:
                        new_lines.append((fragment, "default"))
                else:
                    new_lines.append((fragment, "stdout"))
            new_lines.append(("\n", "stdout"))
        else:
            new_lines.append((indentation + line + "\n", "stdout"))
    return new_lines


def idle_formatter(info, include="friendly_tb"):
    """Formatter that takes care of color definitions."""
    # The explanation for SyntaxError and subclasses states that the
    # location of the error is indicated by --> and ^
    keep_caret = (
        "SyntaxError" in info["shortened_traceback"]
        or "IndentationError" in info["shortened_traceback"]
        or "TabError" in info["shortened_traceback"]
    )
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = ["\n"]
    for item in items_to_show:
        if item == "header":
            continue

        if item in info:
            if "traceback" in item:  # no additional indentation
                result.extend(format_traceback(info[item]))
            elif "source" in item:  # no additional indentation
                result.extend(format_source(info[item], keep_caret))
            elif "header" in item:
                indentation = spacing[repl_indentation[item]]
                result.append((indentation + info[item], "stderr"))
            elif item == "message":  # Highlight error name
                parts = info[item].split(":")
                parts[0] = "`" + parts[0] + "`"
                _info = {item: ":".join(parts)}
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(_info, item, indentation))
            else:
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(info, item, indentation))

    if result == ["\n"]:
        return no_result(info, include)

    return result


def install_in_idle_shell():
    """Installs Friendly-traceback in IDLE's shell so that it can retrieve
    code entered in IDLE's repl.
    Note that this requires Python version 3.10+ since IDLE did not support
    custom excepthook in previous versions of Python.

    Furthermore, Friendly-traceback is bypassed when code entered in IDLE's repl
    raises SyntaxErrors.
    """
    import friendly_traceback

    friendly_traceback.exclude_file_from_traceback(idlelib_run.__file__)
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

    friendly_traceback.install(include="friendly_tb", redirect=idle_writer)
    # Current limitation
    idle_writer("                                WARNING\n", "ERROR")  # noqa
    idle_writer(
        "Friendly-traceback cannot handle SyntaxErrors for code entered in the shell.\n"
    )


def install():
    """Installs Friendly-traceback in the IDLE shell, with a custom formatter.
    For Python versions before 3.10, this is not directly supported, so a
    Friendly console is used instead of IDLE's shell.
    """
    import friendly_traceback

    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_formatter(idle_formatter)
    if sys.version_info >= (3, 10):
        install_in_idle_shell()
    else:
        idle_writer("Friendly-traceback cannot be installed in this version of IDLE.\n")
        idle_writer("Using Friendly's own console instead.\n")
        start_console()


def start_console():
    """Starts a Friendly console with a custom formatter for IDLE"""
    import friendly_traceback  # noqa

    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_formatter(idle_formatter)
    friendly_traceback.set_stream(idle_writer)
    friendly_traceback.start_console()


def run(filename, lang=None, include="friendly_tb", args=None, console=False):
    """This function executes the code found in a python file.

    ``filename`` should be either an absolute path or, it should be the name of a
    file (filename.py) found in the same directory as the file from which ``run()``
    is called.

    If friendly_console is set to ``False`` (the default) and the Python version
    is greater or equal to 3.10, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True``, the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currently only ``en`` (default) and ``fr``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised.

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...


    """
    import friendly_traceback

    _ = current_lang.translate

    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_formatter(idle_formatter)
    friendly_traceback.set_stream(idle_writer)

    filename = Path(filename)
    if not filename.is_absolute():
        frame = inspect.stack()[1]
        # This is the file from which run() is called
        run_filename = Path(frame[0].f_code.co_filename)
        run_dir = run_filename.parent.absolute()
        filename = run_dir.joinpath(filename)

    if not filename.exists():
        print(_("The file {filename} does not exist.").format(filename=filename))
        return

    if sys.version_info >= (3, 10) and not console:
        install_in_idle_shell()
    elif sys.version_info < (3, 10) and console:
        sys.stderr.write(
            "Friendly-traceback cannot be installed in this version of IDLE.\n"
        )
        sys.stderr.write("Using Friendly's own console instead.\n")

    return friendly_traceback.run(
        filename, lang=lang, include=include, args=args, console=console
    )


__all__ = list(helpers.keys())
__all__.append("install")
__all__.append("start_console")
__all__.append("run")
