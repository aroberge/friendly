"""
console_helpers.py
==================

Functions that can be used in a friendly console or in other interactive
environments such as in a Jupyter notebook.

We suggest to use ``dir()`` to see all possible choices as some might
not be listed here.
"""

import sys
import friendly_traceback

from . import debug_helper
from .config import session
from .formatters import items_in_order
from .info_generic import get_generic_explanation
from .path_info import show_paths
from .my_gettext import current_lang


def explain(include="explain"):
    """Shows the previously recorded traceback info again,
    with the specified verbosity level.
    """
    old_include = friendly_traceback.get_include()
    friendly_traceback.set_include(include)
    session.show_traceback_info_again()
    friendly_traceback.set_include(old_include)


def show_info():
    """Debugging tool: shows the complete content of traceback info.

    Prints ``None`` for a given item if it is not present.
    """
    info = session.saved_info if session.saved_info is not None else []

    for item in items_in_order:
        if item in info and info[item].strip():
            print(f"{item}:")
            for line in info[item].split("\n"):
                print("   ", line)
            print()
        else:
            print(f"{item}: None")


def more():
    """Used to display information additional to the minimal traceback,
    with the exception of the generic information.
    Potentially useful for advanced users.
    """
    explain("more")


def what(exception=None, pre=False):
    """If known, shows the generic explanation about a given exception."""
    if exception is None:
        explain("what")
        return

    if hasattr(exception, "__name__"):
        exception = exception.__name__
    result = get_generic_explanation(exception)

    if pre:  # for documentation
        lines = result.split("\n")
        for line in lines:
            session.write_err("    " + line + "\n")
        session.write_err("\n")
    else:
        session.write_err(result)
    return


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


def debug(flag=True):
    """This functions displays the true traceback recorded, that
    includes friendly-traceback's own code.
    It also sets a debug flag for the current session.
    """
    debug_helper.DEBUG = flag
    explain("debug_tb")


def _get_statement():
    """This returns a 'Statement' instance obtained for SyntaxErrors and
    subclasses.

    This is not intended for end-users but is useful in development.
    """
    return session.friendly_traceback.tb_data.statement


def www(search=None, python=False):
    """This uses the ``webbrowser`` module to open a tab (or window) in the
    default browser, linking to a specific url.

    * If no arguments are provided, and no exception has been raised, this opens
      Friendly-traceback documentation.

    * If no arguments are provided, and an exception has been raised, in most
      cases, an internet search will be done using the exception message as the
      search string. In a few cases, Friendly-traceback will link to a
      specific site based on its determination of the cause of the exception.

    * If no search argument is provided, but ``python`` is specified to be ``True``,
      we will have the following:

        * If no exception has been raised, this opens the Python documentation

        * If an exception has been raised, in most cases a search of the Python
          documentation will be done using the exception name as the search term.
          In a few cases, Friendly-traceback will link to a
          specific site based on its determination of the cause of the exception.

    * If a search (string) argument is provided, we have three possibilities:

      * If the ``python`` argument is ``True``, a search will be done in the
        Python documentation site; otherwise
      * if the search term contains the string "friendly" (independent of case),
        Friendly-traceback documentation will open
      * otherwise, an internet search will be done using the search string provided.
    """
    import urllib
    import webbrowser

    _ = current_lang.translate

    if search is not None and not isinstance(search, str):
        sys.stderr.write(
            _("The first argument of `www()` must be either `None` or a string.\n")
        )
        if search is True and not python:
            sys.stderr.write(
                _(
                    "If you wish to open Python's documentation, use\n"
                    "`www(python=True)`.\n"
                )
            )
        return

    quote = urllib.parse.quote  # noqa

    ddg_url = "https://duckduckgo.com?q="
    friendly_url = "https://aroberge.github.io/friendly-traceback-docs/docs/html/"
    python_docs_url = _("https://docs.python.org/3/")
    python_search_url = _("https://docs.python.org/3/search.html?q=")
    info = session.saved_info

    if search is None and not python:  # default search
        if info is None:
            url = friendly_url
        elif "python_link" in info:
            url = info["python_link"]
        else:
            message = info["message"]
            if " (" in message:
                message = message.split("(")[0]
            url = ddg_url + quote(message)
    elif search is None:
        if info is not None and "python_link" in info:
            url = info["python_link"]
        elif info is not None:  # an exception has been raised
            url = python_search_url + session.friendly_traceback.tb_data.exception_name
        else:
            url = python_docs_url
    elif python:
        url = python_search_url + quote(search)
    elif "friendly" in search.lower():
        url = friendly_url
    else:
        url = ddg_url + quote(search)

    try:
        webbrowser.open_new_tab(url)
    except Exception:
        sys.stderr.write(_("The default web browser cannot be used for searching."))


get_lang = friendly_traceback.get_lang
set_lang = friendly_traceback.set_lang
get_include = friendly_traceback.get_include
set_include = friendly_traceback.set_include
show_include_choices = friendly_traceback.show_include_choices

helpers = {
    "explain": explain,
    "what": what,
    "where": where,
    "why": why,
    "more": more,
    "get_lang": get_lang,
    "set_lang": set_lang,
    "get_include": get_include,
    "set_include": set_include,
    "show_include_choices": show_include_choices,
    "hint": hint,
    "friendly_tb": friendly_tb,
    "python_tb": python_tb,
    "debug_tb": debug_tb,
    "debug": debug,
    "show_paths": show_paths,
    "show_info": show_info,
    "_get_statement": _get_statement,
    "www": www,
}


class Friendly:
    """Helper class which can be used in a console if one of the
    helper functions gets redefined.

    For example, we can write Friendly.explain() as equivalent to explain().
    """

    pass


for helper in helpers:
    setattr(Friendly, helper, helpers[helper])

helpers["Friendly"] = Friendly

__all__ = list(helpers.keys())
