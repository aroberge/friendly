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

from importlib import import_module
from pathlib import Path

# Modules
from . import console
from . import debug_helper
from . import formatters
from . import theme
from .my_gettext import current_lang

# Objects from __init__.py
from . import explain_traceback, exclude_file_from_traceback, install
from . import set_formatter, __version__


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
    "--style",
    help="""To use with 'rich' --format option.
    Indicates if the background colour of the console is 'dark' or 'light'.
    The default is 'dark'. The light theme is just a proof of concept.
    You could also try to specify a pygments style - it might work.
    """,
)

parser.add_argument(
    "--include",
    help="""Specifies what content to include by default in the traceback.
    The defaults are 'friendly_tb' if the friendly-console is going to be shown,
    otherwise it is 'explain'.
    """,
)

parser.add_argument(
    "--show-include",
    help="List some available choices for the --include parameter and quits.",
    action="store_true",
)


def warn(text):
    print("   #")
    print(f"   # Warning: {text}")
    print("   #")


def main():
    _ = current_lang.translate
    args = parser.parse_args()
    if args.version:
        print(f"\nFriendly-traceback version {__version__}")
        if not args.source:
            sys.exit()

    if args.show_include:
        show_include_choices()
        sys.exit()

    include = "friendly_tb"
    if args.include:
        include = args.include
    elif args.source:
        include = "explain"

    if args.debug:
        debug_helper.DEBUG = True
        include = "debug_tb"

    install(lang=args.lang, include=include)

    if args.style:
        style = theme.set_theme(args.style)
    else:
        style = "dark"

    use_rich = False
    if args.format:
        format = args.format  # noqa
        if format in ["repl", "pre", "markdown"]:
            set_formatter(format)
        elif format == "rich":
            if not theme.rich_available:
                warn("Rich is not installed.")
                set_formatter("rich", style=style)
            else:
                use_rich = True
        else:
            set_formatter(import_function(args.format))
    elif theme.rich_available:
        use_rich = True
        set_formatter("rich", style=style)  # use by default when available.

    console_defaults = {}
    if args.source is not None:
        filename = Path(args.source)
        if not filename.exists():
            print(
                "\n",
                _("The file {filename} does not exist.").format(filename=args.source),
            )
            return

        exclude_file_from_traceback(runpy.__file__)
        sys.argv = [args.source, *args.args]
        try:
            module_dict = runpy.run_path(args.source, run_name="__main__")
            console_defaults.update(module_dict)
        except Exception:
            explain_traceback()
        if sys.flags.interactive:
            console.start_console(local_vars=console_defaults, use_rich=use_rich)

    else:
        console.start_console(local_vars=console_defaults, use_rich=use_rich)


include_choices = """
The main choices for the --include parameter are:

what:    Explain what a given exception means.
where:   Shows the location of the exception and values of variables
why:     Attempts to explain the cause of an exception
explain: Combines most useful information in a single display

friendly_tb, python_tb, debug_tb: three different choices for the traceback.

The defaults are *friendly_tb* if the friendly-console is going to be shown,
otherwise it is *explain*.

The following lists all the available choices, automatically extracted
from the source code.
"""

third_party_choices = """
Third-party users interested in writing their own formatters
should consult the detailed *items_in_order* list in formatters.py.
They might also find it useful to type `show_info()` in a
friendly-console after an exception has been raised.
"""


def show_include_choices():
    print(include_choices)
    for key in formatters.items_groups:
        print(key)
    print(third_party_choices)


main()
