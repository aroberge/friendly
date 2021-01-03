"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly-traceback
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""

# DEBUG can also be set to True from __main__ or when
# using the debug() command in the console.
import sys

DEBUG = r"users\andre\github\friendly-traceback" in __file__.lower()


def log(text):
    if DEBUG:
        print(text)


def log_error(e=None):
    if DEBUG:
        from . import explain_traceback

        if e is not None:
            print(repr(e))
        for mod in sys.modules:
            if "pytest" in mod:
                return

        explain_traceback()
        sys.exit()
