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

from .version import __version__
from . import console
from . import public_api
from .session import session
from . import friendly_rich


versions = "Friendly-traceback version {}. [Python version: {}]\n".format(
    __version__, platform.python_version()
)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(
        """Friendly-traceback makes Python tracebacks easier to understand.

    {versions}

    If no command line arguments other than -m are specified,
    Friendly-traceback will start an interactive console.
        """.format(
            versions=versions
        )
    ),
)

parser.add_argument(
    "source",
    nargs="?",
    help="""Name of the script to be run as though it was the main module
    run by Python, so that __name__ does equal '__main__'.
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
    help="""Displays the current version.
         """,
    action="store_true",
)

parser.add_argument(
    "--format",
    "--formatter",
    help="""Specifies an output format (pre, markown, markdown_docs, or rich) or
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


def warn(text):
    print("   #")
    print(f"   # Warning: {text}")
    print("   #")


def main():
    console_defaults = {"friendly": public_api.Friendly()}
    args = parser.parse_args()
    if args.version:
        print(f"\nFriendly-traceback version {__version__}")
        if not args.source:
            sys.exit()

    if args.debug:
        session._debug = True
        log_file = os.path.join(os.path.expanduser("~"), "friendly.log")
        with open(log_file, "w", encoding="utf8") as out:
            out.write("Friendly log\n\n")

    include = "minimal"
    if args.source:
        include = "explain"

    public_api.install(lang=args.lang, include=include)

    use_rich = False
    if args.format:
        format = args.format
        if format in ["pre", "markdown"]:
            public_api.set_formatter(format)
        elif format == "rich":
            if not friendly_rich.rich_available:
                warn("Rich is not installed.")
            else:
                use_rich = True
        else:
            public_api.set_formatter(public_api.import_function(args.format))
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

    if args.source is not None:
        public_api.exclude_file_from_traceback(runpy.__file__)
        if sys.flags.interactive:
            try:
                module_dict = runpy.run_path(args.source, run_name="__main__")
                console_defaults.update(module_dict)
            except Exception:
                public_api.explain()
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
