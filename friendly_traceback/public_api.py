"""public_api.py

This module includes all functions that are part of the public API and
can be directly used

    import friendly_traceback
    friendly_traceback.some_function()

instead of

    import friendly_traceback
    friendly_traceback.some_module.some_function()
"""
import sys

from functools import wraps

from .core import state
from .source_cache import cache, highlight_source
from .path_info import (
    exclude_file_from_traceback,
    is_excluded_file,
    include_file_in_traceback,
)


__all__ = [
    "cache",
    "highlight_source",
    "exclude_file_from_traceback",
    "is_excluded_file",
    "include_file_in_traceback",
]
# Note: more content is added to __all__ below


def make_public(f):
    __all__.append(f.__name__)

    @wraps(f)
    def wrapper(*args, **kwds):
        return f(*args, **kwds)

    return wrapper


@make_public
def explain(redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
       information about a given exception than a standard traceback.
       Note that this excludes SystemExit and KeyboardInterrupt which
       are re-raised.

       By default, the output goes to sys.stderr or to some other stream
       set to be the default by another API call.  However, if
          redirect = some_stream
       is specified, the output goes to that stream, but without changing
       the global settings.

       If the string "capture" is given as the value for redirect, the
       output is saved and can be later retrieved by get_output().
    """
    etype, value, tb = sys.exc_info()
    state.explain(etype, value, tb, redirect=redirect)


@make_public
def install(lang=None, redirect=None, level=1):
    """
    Replaces sys.excepthook by friendly_traceback's own version.
    Intercepts, and provides an explanation for all Python exceptions except
    for SystemExist and KeyboardInterrupt.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        level: verbosity level.  See set_level() for details.
    """
    state.install(lang=lang, redirect=redirect, level=level)


@make_public
def get_output(flush=True):
    """Returns the result of captured output as a string which can be
       written anywhere desired.

       By default, flushes all the captured content.
       However, this can be overriden if desired.
    """
    return state.get_captured(flush=flush)


@make_public
def set_formatter(formatter=None):
    """Sets the default formatter. If no argument is given, the default
       formatter, based on the level, is used.

       A custom formatter must accept ``info`` as a required arguments
       as well as arbitrary keyword-based arguments - these are currently
       subject to change but include ``level``.
    """
    state.set_formatter(formatter=formatter)


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
    state.install_gettext(lang)


@make_public
def get_lang():
    """Returns the current language that had been set for translations.

       Note that the value returned may not reflect truly what is being
       see by the end user: if the translations do not exist for that language,
       the default English strings are used.
    """
    return state.lang


@make_public
def set_level(level):
    """Sets the verbosity level to be used. The values are as follows:

            0: Normal Python tracebacks
            1: Default - does not need to be specified
            2: Python tracebacks appear before the friendly display
            3: Python tracebacks appended at the end of the friendly display.
            4: Python traceback followed by basic explanation
            5: Only basic explanation
            9: Python traceback

        The Python traceback for level >= 1 are the simulated version.
        You can use negative values to show the true Python traceback which
        will likely include function calls from friendly-traceback itself.
        Thus level -9 is equivalent to level 0.

        Other values may be available, as we try to find the most useful
        settings for beginners.
    """
    state.set_level(level)


@make_public
def get_level():
    """Returns the verbosity level currently used."""
    return state.level


@make_public
def set_stream(stream):
    """Sets the stream to which the output should be directed.

       If the string "capture" is given as argument, the
       output is saved and can be later retrieved by get_output()."""
    state.set_redirect(redirect=stream)


@make_public
def get_stream():
    """Returns the value of the current stream used for output."""
    return state.write_err


@make_public
def clear_traceback():
    """Clears the existing traceback"""
    state.clear_traceback()


@make_public
def copy_traceback_info(info):
    """Copy the traceback info obtained from another source"""
    state.traceback_info = info


@make_public
def show_traceback_info_again():
    """Shows the traceback info again, on the default stream

    Intended to use with GUI based program, where the user changes
    a verbosity level to view the traceback again.
    """
    state.show_traceback_info_again()
