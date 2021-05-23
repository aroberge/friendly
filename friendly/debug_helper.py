"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""
import sys
import os

# DEBUG is set to True for me. It can also be set to True from __main__ or when
# using the debug() command in the console.

IS_PYDEV = bool(os.environ.get("PYTHONDEVMODE", False))
IS_ANDRE = r"users\andre\github\friendly" in __file__.lower()
DEBUG = IS_PYDEV or IS_ANDRE
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
