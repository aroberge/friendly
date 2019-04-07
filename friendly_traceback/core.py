"""install.py

Just a first draft as proof of concept.
"""

import sys

_CAPTURE = []


def install():
    """
    Replaces sys.excepthook by explain.
    """
    sys.excepthook = explain


def write_err(txt):
    sys.stderr.write(txt)


def explain(etype, value, tb, redirect=None):
    if redirect is not None:
        write_err = redirect

    write_err(str(etype) + "\n")
    write_err(str(value) + "\n")
    write_err(str(tb) + "\n")


def capture(txt):
    _CAPTURE.append(txt)


def get_output(flush=True):
    result = "".join(_CAPTURE)
    if flush:
        _CAPTURE.clear()
    return result
