"""
console_helpers.py
------------------

Functions that can be used in a friendly console or in other interactive
environments such as in a Jupyter notebook.
"""
# NOTE: __all__ is defined at the very bottom of this file
import friendly

from . import debug_helper, __version__
from .config import session
from . import formatters
from .info_generic import get_generic_explanation
from .path_info import show_paths
from .my_gettext import current_lang
from . import theme


def _show_paths_repr():
    _ = current_lang.translate
    return (_("Shows the paths corresponding to synonyms used."),)  # noqa


show_paths.__rich_repr__ = _show_paths_repr


def back():
    """Removes the last recorded traceback item.

    The intention is to allow recovering from a typo when trying interactively
    to find out specific information about a given exception.

    Note that, if the language is changed at some point, going back in time does
    not change the language in which a given traceback information was recorded.
    """
    _ = current_lang.translate
    if not session.saved_info:
        session.write_err(_("Nothing to go back to: no exception recorded.") + "\n")
        return
    if not session.friendly:  # pragma: no cover
        debug_helper.log("Problem: saved info is not empty but friendly is")
    session.saved_info.pop()
    session.friendly.pop()


def _back_repr():
    _ = current_lang.translate
    return (_("Removes the last recorded traceback item."),)  # noqa


back.__rich_repr__ = _back_repr


def explain(include="explain"):
    """Shows the previously recorded traceback info again,
    with the specified verbosity level.
    """
    old_include = friendly.get_include()
    friendly.set_include(include)
    session.show_traceback_info_again()
    friendly.set_include(old_include)


def _explain_repr():
    _ = current_lang.translate
    return (_("Shows all the information about the last traceback."),)  # noqa


explain.__rich_repr__ = _explain_repr


def friendly_tb():
    """Shows the friendly traceback, which includes the hint/suggestion
    if available.
    """
    explain("friendly_tb")


def _friendly_tb_repr():
    _ = current_lang.translate
    return (_("Shows a simplified Python traceback"),)  # noqa


friendly_tb.__rich_repr__ = _friendly_tb_repr


def hint():
    """Shows hint/suggestion if available."""
    explain("hint")


def history():
    """Prints the list of error messages recorded so far."""
    _ = current_lang.translate
    if not session.saved_info:
        session.write_err(_("Nothing to show: no exception recorded.") + "\n")
        return
    session.rich_add_vspace = False
    for info in session.saved_info:
        message = session.formatter(info, include="message").replace("\n", "")
        session.write_err(message)
    session.rich_add_vspace = True


def _history_repr():
    _ = current_lang.translate
    return (_("Shows a list of recorded traceback messages."),)  # noqa


history.__rich_repr__ = _history_repr


def more():
    """Used to display information additional to the minimal traceback,
    with the exception of the generic information.
    Potentially useful for advanced users.
    """
    explain("more")


def _more_repr():
    _ = current_lang.translate
    return (_("Equivalent to what() + where() + why()."),)  # noqa


more.__rich_repr__ = _more_repr


def python_tb():
    """Shows the Python traceback, excluding files from friendly
    itself.
    """
    explain("python_tb")


def _python_tb_repr():
    _ = current_lang.translate
    return (_("Shows a normal Python traceback"),)  # noqa


python_tb.__rich_repr__ = _python_tb_repr


def what(exception=None, pre=False):
    """If known, shows the generic explanation about a given exception."""
    if exception is None:
        explain("what")
        return

    if hasattr(exception, "__name__"):
        exception = exception.__name__
    result = get_generic_explanation(exception)

    if pre:  # for documentation # pragma: no cover
        lines = result.split("\n")
        for line in lines:
            session.write_err("    " + line + "\n")
        session.write_err("\n")
    else:
        session.write_err(result)
    return


def _what_repr():
    _ = current_lang.translate
    return (_("Shows the generic meaning of a given exception"),)  # noqa


what.__rich_repr__ = _what_repr


def where():
    """Shows the information about where the exception occurred"""
    explain("where")


def _where_repr():
    _ = current_lang.translate
    return (_("Shows where an exception was raised."),)  # noqa


where.__rich_repr__ = _where_repr


def why():
    """Shows the likely cause of the exception."""
    explain("why")


def _why_repr():
    _ = current_lang.translate
    return (_("Shows the likely cause of the exception."),)  # noqa


why.__rich_repr__ = _why_repr


def www(search=None, python=False):  # pragma: no cover
    """This uses the ``webbrowser`` module to open a tab (or window) in the
    default browser, linking to a specific url.

    * If no arguments are provided, and no exception has been raised, this opens
      Friendly's documentation.

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
        session.write_err(
            _("The first argument of `www()` must be either `None` or a string.\n")
        )
        if search is True and not python:
            session.write_err(
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
    info = session.saved_info[-1] if session.saved_info else None
    if search is None and not python:  # default search
        if info is None:
            url = friendly_url
        elif "python_link" in info:
            url = info["python_link"]
        else:
            # avoid including quotes around variable names as this would
            # make them be misinterpreted as important by search engines
            message = info["message"].replace("'", "")
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
    except Exception:  # noqa
        session.write_err(_("The default web browser cannot be used for searching."))


def _www_repr():
    _ = current_lang.translate
    return (_("Opens a web browser at a useful location."),)  # noqa


www.__rich_repr__ = _www_repr


get_lang = friendly.get_lang
set_lang = friendly.set_lang
get_include = friendly.get_include
set_include = friendly.set_include
set_formatter = friendly.set_formatter


def _get_lang_repr():
    _ = current_lang.translate
    return (_("Returns the language currently used."),)  # noqa


def _set_lang_repr():
    _ = current_lang.translate
    return (_("Sets the language to be used."),)  # noqa


def _get_include_repr():
    _ = current_lang.translate
    return (
        _("Returns the current value used for items to include by default."),
    )  # noqa


def _set_include_repr():
    _ = current_lang.translate
    return (_("Sets the items to show when an exception is raised."),)  # noqa


def _set_formatter_repr():
    _ = current_lang.translate
    return (_("Sets the formatter to use for display."),)  # noqa


get_include.__rich_repr__ = _get_include_repr
set_include.__rich_repr__ = _set_include_repr
get_lang.__rich_repr__ = _get_lang_repr
set_lang.__rich_repr__ = _set_lang_repr
set_formatter.__rich_repr__ = _set_formatter_repr

# ===== Debugging functions are not unit tested by choice =====


def _debug_tb():  # pragma: no cover
    """Shows the true Python traceback, which includes
    files from friendly itself.
    """
    explain("debug_tb")


def _get_exception():  # pragma: no cover
    """Debugging tool: returns the exception instance or None if no exception
    has been raised.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_exc_instance"]


def _get_frame():  # pragma: no cover
    """This returns the frame in which the exception occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_frame"]


def _get_statement():  # pragma: no cover
    """This returns a 'Statement' instance obtained for SyntaxErrors and
    subclasses.  Such a Statement instance contains essentially all
    the known information about the statement where the error occurred.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    if isinstance(session.saved_info[-1]["_exc_instance"], SyntaxError):
        return session.friendly[-1].tb_data.statement
    print("No statement: not a SyntaxError.")
    return


def _get_tb_data():  # pragma: no cover
    """This returns the TracebackData instance containing all the
    information we have obtained.

    This is not intended for end-users but is useful in development.
    """
    if not session.saved_info:
        print("Nothing to show: no exception recorded.")
        return
    info = session.saved_info[-1]
    return info["_tb_data"]


def _set_debug(flag=True):  # pragma: no cover
    """This functions displays the true traceback recorded, that
    includes friendly's own code.
    It also sets a debug flag for the current session.
    """
    debug_helper.DEBUG = flag
    explain("debug_tb")


def _show_info():  # pragma: no cover
    """Debugging tool: shows the complete content of traceback info.

    Prints ``None`` for a given item if it is not present.
    """
    info = session.saved_info[-1] if session.saved_info else []

    for item in formatters.items_in_order:
        if item in info and info[item].strip():
            print(f"{item}:")
            for line in info[item].strip().split("\n"):
                print("   ", line)
            print()
        else:
            print(f"{item}: None")


basic_helpers = {  # Will appear in basic help
    "back": back,
    "history": history,
    "explain": explain,
    "what": what,
    "where": where,
    "why": why,
    "more": more,
    "set_lang": set_lang,
    "friendly_tb": friendly_tb,
    "python_tb": python_tb,
    "show_paths": show_paths,
    "www": www,
}

other_helpers = {
    "hint": hint,
    "get_lang": get_lang,
    "get_include": get_include,
    "set_include": set_include,
    "set_formatter": set_formatter,
}

helpers = {**basic_helpers, **other_helpers}

_debug_helpers = {
    "_debug_tb": _debug_tb,
    "_show_info": _show_info,
    "_get_exception": _get_exception,
    "_get_frame": _get_frame,
    "_get_statement": _get_statement,
    "_get_tb_data": _get_tb_data,
    "_set_debug": _set_debug,
}


class FriendlyHelpers:
    """Helper class which can be used in a console if one of the
    helper functions gets redefined.

    For example, we can write Friendly.explain() as equivalent to explain().
    """

    version = __version__

    def __init__(self, color_schemes=None):
        _include = list(basic_helpers)
        if color_schemes is not None:
            _include.extend(color_schemes)
        _include = sorted(_include)  # first alphabetically
        # then by word length, as it is easier to read.
        self.include_in_rich_repr = sorted(_include, key=len)
        self.__class__.__name__ = "Friendly"  # For a nicer Rich repr

    def __rich_repr__(self):
        """Shows a brief description in the default language of what
        each 'basic' function/method does.

        'Advanced' and debugging helper functions are not included
        in the display.
        """
        _ = current_lang.translate
        text = _("Use `help(Friendly)` and `dir(Friendly)` for more information.")
        md = theme.friendly_rich.Markdown(
            text, inline_code_lexer="python", code_theme=theme.CURRENT_THEME
        )
        session.console.print("", md, "")
        yield _("Object with many methods, including:")
        for item in self.include_in_rich_repr:
            yield item, getattr(Friendly, item)


for helper in _debug_helpers:
    setattr(FriendlyHelpers, helper, staticmethod(_debug_helpers[helper]))
for helper in helpers:
    setattr(FriendlyHelpers, helper, staticmethod(helpers[helper]))

# == Local version; something like the following needs
# to be done in each specialized versions (e.g. Mu, Idle, IPython, etc.)


class _FriendlyHelpers(FriendlyHelpers):  # local version
    pass


def dark():  # pragma: no cover
    """Synonym of set_formatter('dark') designed to be used
    within iPython/Jupyter programming environments or at a terminal.
    """
    set_formatter("dark")


def _dark_repr():
    _ = current_lang.translate
    return (_("Colour scheme designed for a black background."),)  # noqa


dark.__rich_repr__ = _dark_repr


def light():  # pragma: no cover
    """Synonym of set_formatter('light') designed to be used
    within iPython/Jupyter programming environments or at a terminal.
    """
    set_formatter("light")


def _light_repr():
    _ = current_lang.translate
    return (_("Colour scheme designed for a white background."),)  # noqa


light.__rich_repr__ = _light_repr

default_color_schemes = {"dark": dark, "light": light}

Friendly = _FriendlyHelpers(default_color_schemes)
for scheme in default_color_schemes:
    setattr(_FriendlyHelpers, scheme, staticmethod(default_color_schemes[scheme]))

helpers["Friendly"] = Friendly

__all__ = list(helpers.keys())
__all__.extend(list(default_color_schemes))
