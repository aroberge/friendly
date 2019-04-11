"""
invocation.py
---------------

Info to be written -- currently

"""
import argparse
import runpy
import sys

from . import console
from . import core
from . import version  # noqa


parser = argparse.ArgumentParser(
    description="""Friendly-traceback makes Python tracebacks easier to
        understand.
        """
)
parser.add_argument("source")

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
    # console_dict = {}
    args = parser.parse_args()
    core.install(lang=args.lang)

    if args.source is not None:
        if sys.flags.interactive:
            if args.as_main:
                module = runpy.run_module(args.source, run_name="__main__")
            else:
                module = __import__(args.source)
            module_dict = {}
            for var in dir(module):
                module_dict[var] = getattr(module, var)
            console.start_console(local_vars=module_dict)
        elif args.as_main:
            runpy.run_module(args.source, run_name="__main__")
        else:
            module = __import__(args.source)
    else:
        console.start_console()


if "-m" in sys.argv:
    main()
