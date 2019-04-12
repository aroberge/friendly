"""
invocation.py
---------------

Info to be written -- currently

"""
import argparse
import sys

from . import console
from . import core
from . import version  # noqa


parser = argparse.ArgumentParser(
    description="""Friendly-traceback makes Python tracebacks easier to
        understand.
        """
)
parser.add_argument("source", nargs="?")

parser.add_argument(
    "--lang",
    help="""This sets the language used by Friendly-tracebacks.
            Usually this is a two-letter code such as 'fr' for French.
         """,
)

parser.add_argument(
    "--as_main",
    help="""Runs the program as though it was the main script.
            In case of problems with the code, it can lead to some difficult
            to understand tracebacks.
         """,
    action="store_true",
)


def main():
    console_dict = {"set_lang": core.set_lang}
    args = parser.parse_args()
    core.install(lang=args.lang)

    if args.source is not None:
        if sys.flags.interactive:
            if args.as_main:
                module_dict = core.run_script(args.source)
            else:
                module = __import__(args.source)
                module_dict = {}
                for var in dir(module):
                    module_dict[var] = getattr(module, var)
            console_dict.update(module_dict)
            console.start_console(local_vars=console_dict)
        elif args.as_main:
            core.run_script(args.source)
        else:
            module = __import__(args.source)
    else:
        console.start_console()


if "-m" in sys.argv:
    main()
