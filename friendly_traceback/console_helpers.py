"""
console_helpers.py
==================

Functions that can be used in a friendly console or in other interactive
environments such as in a Jupyter notebook.

"""
# TODO: add unit tests for each of these

import friendly_traceback

from . import debug_helper
from .config import session
from .info_generic import get_generic_explanation
from .path_info import show_paths


def explain(include="explain"):
    """Shows the previously recorded traceback info again,
    with the specified verbosity level.
    """
    old_include = friendly_traceback.get_include()
    friendly_traceback.set_include(include)
    session.show_traceback_info_again()
    friendly_traceback.set_include(old_include)


def show_info():
    """Debugging tool: shows the complete content of traceback info."""
    if session.saved_info is None:
        print("No recorded traceback\n")
        return
    print("Recorded traceback information:\n")
    if session.use_rich:  # will automatically pretty print
        return session.saved_info

    for item in session.saved_info:
        print(f"{item}: {session.saved_info[item]}")


def more():
    """Used to display information additional to the minimal traceback,
    with the exception of the generic information.
    Potentially useful for advanced users.
    """
    explain("more")


def what(exception=None):
    """If known, shows the generic explanation about a given exception."""
    if exception is not None:
        if hasattr(exception, "__name__"):
            exception = exception.__name__
        result = get_generic_explanation(exception)
        session.write_err(result)
        return
    explain("what")


def where():
    """Shows the information about where the exception occurred"""
    explain("where")


def why():
    """Shows the likely cause of the exception."""
    explain("why")


def hint():
    """Shows hint/suggestion if available."""
    explain("hint")


def friendly_tb():
    """Shows the friendly traceback, which includes the hint/suggestion
    if available.
    """
    explain("friendly_tb")


def python_tb():
    """Shows the Python traceback, excluding files from friendly-traceback
    itself.
    """
    explain("python_tb")


def debug_tb():
    """Shows the true Python traceback, which includes
    files from friendly-traceback itself.
    """
    explain("debug_tb")


def debug():
    """This functions displays the true traceback recorded, that
    includes friendly-traceback's own code.
    It also adds the suggestion/hint from friendly-traceback
    and sets a debug flag for the current session.
    """
    debug_helper.DEBUG = True
    explain("debug_tb")


helpers = {
    "explain": explain,
    "what": what,
    "where": where,
    "why": why,
    "more": more,
    "get_lang": friendly_traceback.get_lang,
    "set_lang": friendly_traceback.set_lang,
    "get_include": friendly_traceback.get_include,
    "set_include": friendly_traceback.set_include,
    "show_include_choices": friendly_traceback.show_include_choices,
    "hint": hint,
    "friendly_tb": friendly_tb,
    "python_tb": python_tb,
    "debug_tb": debug_tb,
    "debug": debug,
    "show_paths": show_paths,
    "show_info": show_info,
}


class Friendly:
    """Helper class which can be used in a console if one of the
    helper functions gets redefined.

    For example, we can write Friendly.explain() as equivalent to explain().
    """

    pass


for item in helpers:
    setattr(Friendly, item, helpers[item])

helpers["Friendly"] = Friendly
