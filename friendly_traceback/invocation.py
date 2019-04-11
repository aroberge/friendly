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
parser.add_argument(
    "-s",
    "--source",
    help="""Source file to be transformed and executed.
            It is assumed that it can be imported.
            Format: path.to.file -- Do not include an extension.
         """,
)
parser.add_argument(
    "--lang",
    help="""This sets the language used by Friendly-tracebacks.
            Usually this is a two-letter code such as 'fr' for French.
         """,
)


def main():
    # console_dict = {}
    args = parser.parse_args()
    core.install(lang=args.lang)

    if args.source is not None:
        main_module = __import__(args.source)
        if sys.flags.interactive:
            main_dict = {}
            for var in dir(main_module):
                main_dict[var] = getattr(main_module, var)
            console.start_console(local_vars=main_dict)
    else:
        console.start_console()


if "-m" in sys.argv:
    main()
