"""public_api.py

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

"""
from functools import wraps

from . import core

# Make functions from other modules directly available from here.
from .editors_helper import advanced_check_syntax, check_syntax, exec_code, run
from .session import session
from .source_cache import cache, highlight_source
from .path_info import (
    exclude_file_from_traceback,
    is_excluded_file,
    include_file_in_traceback,
)

__version__ = "0.0.35a"
__all__ = [
    "advanced_check_syntax",
    "cache",
    "check_syntax",
    "exclude_file_from_traceback",
    "exec_code",
    "highlight_source",
    "include_file_in_traceback",
    "is_excluded_file",
    "run",
    "__version__",
]


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
    core.explain_traceback(redirect=redirect)


@make_public
def install(lang=None, redirect=None, verbosity=None, level=None):
    """
    Replaces ``sys.excepthook`` by friendly_traceback's own version.
    Intercepts, and provides an explanation for all Python exceptions except
    for ``SystemExist`` and ``KeyboardInterrupt``.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        verbosity: verbosity level.  See set_verbosity() for details.

        level: deprecated; use verbosity instead.

        hook: exception_hook - if one wants to experiment using
              a different one.
    """
    # TODO: check validity here instead of in sessions.py

    session.install(lang=lang, redirect=redirect, verbosity=verbosity, level=level)


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
def set_formatter(formatter=None):
    """Sets the default formatter. If no argument is given, the default
       formatter, based on the level, is used.

       A custom formatter must accept ``info`` as a required arguments
       as well as arbitrary keyword-based arguments - these are currently
       subject to change but include ``level``.
    """
    # TODO: change level to verbosity
    session.set_formatter(formatter=formatter)


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
def set_level(level):
    """Deprecated; use set_verbosity() instead.
    """
    set_verbosity(level)


@make_public
def set_verbosity(level):
    """Sets the verbosity level to be used. These settings might be ignored
       by custom formatters.

       Vocabulary examples ::
           Generic explanation: A NameError occurs when ...
           Specific explanation: In your program, the unknown name is ...

       The values are as follows::

            0: Normal Python tracebacks: friendly_traceback is disabled.
            1: Default - does not need to be specified. The normal Python
               traceback is not included in the output.
            2: Python tracebacks appear before the output of level 1.
            3: Python tracebacks appended at the end of the output of level 1.
            4: Same as 1, but generic explanation is not included
            5: Same as 2, but generic explanation is not included
            6: Same as 3, but generic explanation is not included
            7: (Subject to change) Python tracebacks followed
               by specific information.
            8: Minimal display of relevant information,
               suitable for console use by advanced programmers.
            9: Simulated Python traceback: see the documentation.
    """
    session.set_verbosity(level)


@make_public
def get_level():
    """Deprecated: use get_verbosity() instead."""
    return get_verbosity()


@make_public
def get_verbosity():
    """Returns the verbosity level currently used."""
    return session.level


@make_public
def set_stream(stream):
    """Sets the stream to which the output should be directed.

       If the string ``"capture"`` is given as argument, the
       output is saved and can be later retrieved by ``get_output()``."""
    session.set_redirect(redirect=stream)


@make_public
def get_stream():
    """Returns the value of the current stream used for output."""
    return session.write_err


@make_public
def clear_traceback():
    """Clears the existing traceback."""
    session.clear_traceback()


@make_public
def copy_traceback_info(info):
    """Copy the traceback info obtained from another source."""
    session.traceback_info = info


@make_public
def show_again():
    """Shows the traceback info again, on the default stream.

    Primarily intended to be used when the user changes
    a verbosity level to view the last computed traceback in a given language.
    """
    session.show_traceback_info_again()
