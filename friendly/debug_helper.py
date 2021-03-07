"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly-traceback
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""
import sys

# DEBUG is set to True for me. It can also be set to True from __main__ or when
# using the debug() command in the console.

DEBUG = r"users\andre\github\friendly-traceback" in __file__.lower()
EXIT = False


def log(text):
    if DEBUG:
        print(text)


def log_error(exc=None):
    global EXIT
    if DEBUG:
        from . import explain_traceback

        if exc is not None:
            print(repr(exc))
        if not EXIT:
            EXIT = True
            explain_traceback()
        log("Fatal error - aborting")
        sys.exit()
