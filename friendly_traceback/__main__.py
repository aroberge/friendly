"""
main.py
---------------

Sets up the various options when Friendly-traceback is invoked from the
command line. You can find more details by doing::

    python -m friendly_traceback -h

"""
import argparse
import platform
import runpy
import sys

from .version import __version__
from . import console
from . import public_api
from .session import session
from .friendly_rich import rich_available
from .my_gettext import current_lang


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

    Note: the values of the verbosity level described below are:

        1: Default - does not need to be specified. The normal Python
           traceback is not included in the output.
        2: Python tracebacks appear before the output of level 1.
        3: Python tracebacks appended at the end of the output of level 1.
        4: Same as 1, but generic explanation is not included
        5: Same as 2, but generic explanation is not included
        6: Same as 3, but generic explanation is not included
        7: Minimal friendly display of relevant information,
           suitable for console use by advanced programmers.
        8: (Subject to change) Python tracebacks followed
           by specific information.
        9: Python traceback
        0: Python traceback that also includes calls to friendly-traceback.

       Vocabulary examples:
           Generic explanation: A NameError occurs when ...
           Specific explanation: In your program, the unknown name is ...
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
    "--verbosity",
    "--level",
    type=int,
    default=1,
    help="""This sets the "verbosity" level, that is the amount of information
            provided. ("level" is deprecated and will be removed.)
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
    default="pre",
    help="""Specifies an output format (pre, markown, markdown_docs, or rich) or
    a custom formatter function, as a dotted path.

    For example: --formatter friendly_traceback.formatters.markdown is
    equivalent to --formatter markdown
    """,
)


def main():
    _ = current_lang.translate

    console_defaults = {"friendly": public_api.Friendly()}
    args = parser.parse_args()
    if args.version:
        print(f"Friendly-traceback version {__version__}")
        sys.exit()

    public_api.install(lang=args.lang, verbosity=args.verbosity)

    use_rich = False
    if args.format:
        format = args.format
        if format in ["pre", "markdown"]:
            public_api.set_formatter(format)
        elif format == "rich":
            if not rich_available:
                print(_("\n    Rich is not installed.\n\n"))
            else:
                use_rich = True
                session.use_rich = True
                public_api.set_formatter("rich")
        else:
            public_api.set_formatter(public_api.import_function(args.format))

    if args.source is not None:
        public_api.exclude_file_from_traceback(runpy.__file__)
        if sys.flags.interactive:
            try:
                module_dict = runpy.run_path(args.source, run_name="__main__")
                console_defaults.update(module_dict)
            except Exception:
                public_api.explain()
            console.start_console(local_vars=console_defaults, use_rich=use_rich)
        else:
            sys.argv = [args.source, *args.args]
            runpy.run_path(args.source, run_name="__main__")
    else:
        console.start_console(local_vars=console_defaults, use_rich=use_rich)


main()
