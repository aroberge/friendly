"""
console_helpers.py
------------------

Functions that can be used in a friendly console or in other interactive
environments such as in a Jupyter notebook.
"""

import sys
import friendly

from . import debug_helper
from .config import session
from .formatters import items_in_order
from .info_generic import get_generic_explanation
from .path_info import show_paths
from .my_gettext import current_lang


def back():
    """Removes the last recorded traceback item.

    The intention is to allow recovering from a typo when trying interactively
    to find out specific information about a given exception.

    Note that, if the language is changed at some point, going back in time does
    not change the language in which a given traceback information was recorded.
    """
    _ = current_lang.translate
    if not session.saved_info:
        print(_("Nothing to go back to: no exception recorded."))
        return
    if not session.friendly:
        debug_helper.log("Problem: saved info is not empty but friendly is")
    session.saved_info.pop()
    session.friendly.pop()


def history():
    """Prints the list of error messages recorded so far."""
    _ = current_lang.translate
    if not session.saved_info:
        print(_("Nothing to show: no exception recorded."))
        return
    session.rich_add_vspace = False
    for info in session.saved_info:
        message = session.formatter(info, include="message").replace("\n", "")
        session.write_err(message)
    session.rich_add_vspace = True


def explain(include="explain"):
    """Shows the previously recorded traceback info again,
    with the specified verbosity level.
    """
    old_include = friendly.get_include()
    friendly.set_include(include)
    session.show_traceback_info_again()
    friendly.set_include(old_include)


def show_info():
    """Debugging tool: shows the complete content of traceback info.

    Prints ``None`` for a given item if it is not present.
    """
    info = session.saved_info[-1] if session.saved_info else []

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
    """Shows the Python traceback, excluding files from friendly
    itself.
    """
    explain("python_tb")


def debug_tb():
    """Shows the true Python traceback, which includes
    files from friendly itself.
    """
    explain("debug_tb")


def debug(flag=True):
    """This functions displays the true traceback recorded, that
    includes friendly's own code.
    It also sets a debug flag for the current session.
    """
    debug_helper.DEBUG = flag
    explain("debug_tb")


def _get_statement():
    """This returns a 'Statement' instance obtained for SyntaxErrors and
    subclasses.

    This is not intended for end-users but is useful in development.
    """
    _ = current_lang.translate
    if not session.saved_info:
        print(_("Nothing to show: no exception recorded."))
        return
    return session.friendly[-1].tb_data.statement


def www(search=None, python=False):
    """This uses the ``webbrowser`` module to open a tab (or window) in the
    default browser, linking to a specific url.

    * If no arguments are provided, and no exception has been raised, this opens
      Friendly documentation.

    * If no arguments are provided, and an exception has been raised, in most
      cases, an internet search will be done using the exception message as the
      search string. In a few cases, Friendly will link to a
      specific site based on its determination of the cause of the exception.

    * If no search argument is provided, but ``python`` is specified to be ``True``,
      we will have the following:

        * If no exception has been raised, this opens the Python documentation

        * If an exception has been raised, in most cases a search of the Python
          documentation will be done using the exception name as the search term.
          In a few cases, Friendly will link to a
          specific site based on its determination of the cause of the exception.

    * If a search (string) argument is provided, we have three possibilities:

      * If the ``python`` argument is ``True``, a search will be done in the
        Python documentation site; otherwise
      * if the search term contains the string "friendly" (independent of case),
        Friendly documentation will open
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
    friendly_url = "https://aroberge.github.io/friendly-docs/docs/html/"
    python_docs_url = _("https://docs.python.org/3/")
    python_search_url = _("https://docs.python.org/3/search.html?q=")
    if session.saved_info:
        info = session.saved_info[-1]
    else:
        info = None

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
            url = python_search_url + session.friendly.tb_data.exception_name
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


get_lang = friendly.get_lang
set_lang = friendly.set_lang
get_include = friendly.get_include
set_include = friendly.set_include
set_formatter = friendly.set_formatter

helpers = {
    "back": back,
    "history": history,
    "explain": explain,
    "what": what,
    "where": where,
    "why": why,
    "more": more,
    "get_lang": get_lang,
    "set_lang": set_lang,
    "get_include": get_include,
    "set_include": set_include,
    "hint": hint,
    "friendly_tb": friendly_tb,
    "python_tb": python_tb,
    "debug_tb": debug_tb,
    "debug": debug,
    "show_paths": show_paths,
    "show_info": show_info,
    "set_formatter": set_formatter,
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
    setattr(Friendly, helper, staticmethod(helpers[helper]))

helpers["Friendly"] = Friendly

__all__ = list(helpers.keys())
