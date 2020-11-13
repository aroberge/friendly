"""
public_api.py
-------------

With the exception of some Friendly-console
related classes or functions, this module includes **all** the functions
that are part of the public API and can be directly used, as in::

    import friendly_traceback
    friendly_traceback.some_function()

instead of::

    import friendly_traceback
    friendly_traceback.public_api.some_function()
    # or
    friendly_traceback.some_inner_module.some_function()

If your code requires access to functions or classes that are not
made available here and are not part of Friendly-console, please
file an issue.
"""
from functools import wraps
from importlib import import_module

from .config import session
from . import info_generic

# Make functions from other modules directly available from here.
from .editors_helper import run

# from .formatters import tb_items_to_show
from .path_info import exclude_file_from_traceback

__all__ = ["exclude_file_from_traceback", "run"]


def make_public(f):
    """Decorator used to add functions to __all__"""
    __all__.append(f.__name__)

    @wraps(f)
    def wrapper(*args, **kwds):
        return f(*args, **kwds)

    return wrapper


@make_public
def explain(redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
    information about a given exception than a standard traceback.
    Note that this excludes ``SystemExit`` and ``KeyboardInterrupt``
    which are re-raised.

    By default, the output goes to ``sys.stderr`` or to some other stream
    set to be the default by another API call. However, if::

       redirect = some_stream

    is specified, the output goes to that stream, but without changing
    the global settings.

    If the string ``"capture"`` is given as the value for ``redirect``, the
    output is saved and can be later retrieved by ``get_output()``.
    """
    session.explain_traceback(redirect=redirect)


@make_public
def install(lang=None, redirect=None, include="explain", level=None):
    """
    Replaces ``sys.excepthook`` by friendly_traceback's own version.
    Intercepts, and provides an explanation for all Python exceptions except
    for ``SystemExist`` and ``KeyboardInterrupt``.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        include: controls the amout of information displayed.
        See set_include() for details.

        level: deprecated; use verbosity instead.
    """
    if level is not None:
        print("Friendly-traceback: level is no longer supported")
        print("The documentation needs to be updated to reflect this change.")
    session.install(lang=lang, redirect=redirect, include=include)


@make_public
def uninstall():
    """Resets sys.excepthook to Python's default"""
    session.uninstall()


@make_public
def is_installed():
    """Returns True if Friendly-traceback is installed, False otherwise"""
    return session.installed


@make_public
def get_output(flush=True):
    """Returns the result of captured output as a string which can be
    written anywhere desired.

    By default, flushes all the captured content.
    However, this can be overriden if desired.
    """
    return session.get_captured(flush=flush)


@make_public
def set_formatter(formatter=None, **kwds):
    """Sets the default formatter. If no argument is given, the default
    formatter is used.

    A custom formatter must accept ``info`` as a required arguments
    as well an additional argument whose value is subject to change.
    See formatters.py for details.
    """
    session.set_formatter(formatter=formatter, **kwds)


@make_public
def get_what(exception_name, lang=None):
    """Given an exception name as a string argument,
    returns what this exception means, also known as the
    generic explanation elsewhere in this package.

    Something like:

        A `RecursionError` is raised when a function calls itself ...

    If argument lang is specified, the information is provided
    in that language (if available) without changing the overall
    default language used.
    """
    if lang is not None:
        old_lang = get_lang()
        set_lang(lang)
    result = info_generic.get_generic_explanation(exception_name)
    if lang is not None:
        set_lang(old_lang)
    return result


# =========================================================================
# Below, we have many set_X()/get_X() pairs. The only reason why we include
# the get_X() type of functions is to make it possible to make some
# temporary changes, i.e.
#
#     saved = get_x()
#     set_X(something)
#     do_something()
#     set_X(saved)
# =========================================================================


@make_public
def set_lang(lang):
    """Sets the language to be used by gettext.

    If no translations exist for that language, the original
    English strings will be used.
    """
    session.install_gettext(lang)


@make_public
def get_lang():
    """Returns the current language that had been set for translations.

    Note that the value returned may not reflect truly what is being
    see by the end user: if the translations do not exist for that language,
    the default English strings are used.
    """
    return session.lang


@make_public
def set_include(include):
    "placeholder docstring"
    session.set_include(include)


@make_public
def get_include():
    "placeholder docstring"
    return session.get_include()


@make_public
def set_stream(redirect=None):
    """Sets the stream to which the output should be directed.

    If the string ``"capture"`` is given as argument, the
    output is saved and can be later retrieved by ``get_output()``.

    If no argument is given, the default stream (stderr) is set.
    """
    session.set_redirect(redirect=redirect)


@make_public
def get_stream():
    """Returns the value of the current stream used for output."""
    return session.write_err


@make_public
def show_again():
    """Shows the previously recorded traceback info again, on the default stream.

    Primarily intended to be used when the user changes
    a verbosity level to view the last computed traceback
    in a given language.
    """
    session.show_traceback_info_again()


@make_public
def quote(text):
    """Surrounds text by single quote, or by backquote if formatter
    is markdown type.
    """
    return session.quote(text)


@make_public
def import_function(dotted_path: str) -> type:
    """Import a function from a module, given its dotted path."""
    # Required for --formatter flag
    # Used by HackInScience.org
    try:
        module_path, function_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, function_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" function' % (module_path, function_name)
        ) from err


# -----------------------------------------
#   Deprecated functions
# -----------------------------------------


@make_public
def set_level(verbosity_level):
    """Deprecated. Details about new API to be provided later."""
    print("friendly-traceback set_level is deprecated; defaults will be used.")
    set_include("explain")
