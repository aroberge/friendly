"""
main.py
---------------

Sets up the various options when Friendly-traceback is invoked from the
command line. You can find more details by doing::

    python -m friendly_traceback -h

"""
import argparse
import os.path
import platform
import runpy
import sys

from importlib import import_module

# Importing modules
from . import console
from . import friendly_rich

# Importing objects from __init__.py
from . import explain_traceback, exclude_file_from_traceback, install
from . import session, set_formatter, __version__


versions = "Friendly-traceback version {}. [Python version: {}]\n".format(
    __version__, platform.python_version()
)


def import_function(dotted_path: str) -> type:
    """Import a function from a module, given its dotted path.

    This is a utility function currently used when a custom formatter
    is used using a command line argument::

        python -m friendly_traceback --format custom_formatter
    """
    # Used by HackInScience.org
    try:
        module_path, function_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, function_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" function' % (module_path, function_name)
        ) from err


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(
        """Friendly-traceback makes Python tracebacks easier to understand.

    {versions}

    If no source is given Friendly-traceback will start an interactive console.
        """.format(
            versions=versions
        )
    ),
)

parser.add_argument(
    "source",
    nargs="?",
    help="""Name of the Python script (path/to/my_program.py)
    to be run as though it was the main module, so that its
    __name__ does equal '__main__'.
    """,
)

parser.add_argument(
    "args",
    nargs="*",
    help="""Optional arguments to give to the script specified by source.
         """,
)

parser.add_argument(
    "--lang",
    default="en",
    help="""This sets the language used by Friendly-tracebacks.
            Usually this is a two-letter code such as 'fr' for French.
         """,
)

parser.add_argument(
    "--version",
    help="""Only displays the current version.
         """,
    action="store_true",
)

parser.add_argument(
    "--format",
    "--formatter",
    help="""Specifies an output format (repl, pre, markown, markdown_docs, or rich) or
    a custom formatter function, as a dotted path. By default, the console
    will use Rich if it is available.

    For example: --formatter friendly_traceback.formatters.markdown is
    equivalent to --formatter markdown
    """,
)


parser.add_argument("--debug", help="""For developer use.""", action="store_true")

parser.add_argument(
    "--theme",
    help="""To use with 'rich' --format option.
    Indicates if the background colour of the console is 'dark' or 'light'.
    The default is 'dark'. The light theme is just a proof of concept.
    """,
)

parser.add_argument(
    "--include",
    help="""Specifies what content to include by default in the traceback.
    The defaults are 'friendly_tb' if the friendly-console is going to be shown,
    otherwise it is 'explain'.
    See the documentation for more details.
    """,
)


def warn(text):
    print("   #")
    print(f"   # Warning: {text}")
    print("   #")


def main():
    args = parser.parse_args()
    if args.version:
        print(f"\nFriendly-traceback version {__version__}")
        if not args.source:
            sys.exit()

    include = "friendly_tb"
    if args.include:
        include = args.include
    elif args.source:
        include = "explain"

    if args.debug:
        session._debug = True
        log_file = os.path.join(os.path.expanduser("~"), "friendly.log")
        with open(log_file, "w", encoding="utf8") as out:
            out.write("Friendly log\n\n")
        include = "debug_tb"

    install(lang=args.lang, include=include)

    use_rich = False
    if args.format:
        format = args.format
        if format in ["repl", "pre", "markdown"]:
            set_formatter(format)
        elif format == "rich":
            if not friendly_rich.rich_available:
                warn("Rich is not installed.")
            else:
                use_rich = True
        else:
            set_formatter(import_function(args.format))
    elif friendly_rich.rich_available:
        use_rich = True

    theme = "dark"
    if use_rich:
        if args.theme == "light":
            theme = "light"
            warn("light theme is just a proof of concept.")
        elif args.theme not in [None, "dark"]:
            warn(f"unknown theme '{args.theme}'.")
        session.set_formatter("rich", theme=theme)
    elif args.theme is not None:
        warn("theme argument ignored.")

    console_defaults = {}
    if args.source is not None:
        exclude_file_from_traceback(runpy.__file__)
        if sys.flags.interactive:
            try:
                module_dict = runpy.run_path(args.source, run_name="__main__")
                console_defaults.update(module_dict)
            except Exception:
                explain_traceback()
            console.start_console(
                local_vars=console_defaults, use_rich=use_rich, theme=theme
            )
        else:
            sys.argv = [args.source, *args.args]
            runpy.run_path(args.source, run_name="__main__")
    else:
        console.start_console(
            local_vars=console_defaults, use_rich=use_rich, theme=theme
        )


main()
