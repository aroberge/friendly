"""Need to add docstring"""

import sys

valid_version = sys.version_info.major >= 3 and sys.version_info.minor >= 6

if not valid_version:
    print("Python 3.6 or newer is required.")
    sys.exit()

del valid_version

# ===========================================

from importlib import import_module
import warnings as _warnings


from .version import __version__  # noqa
from .path_info import exclude_file_from_traceback  # noqa
from .config import session

from . import editors_helper
from . import friendly_rich

# Ensure that warnings are not shown to the end user, as they could
# cause confusion.  Eventually, we might want to interpret them like
# we do for Exceptions.
_warnings.simplefilter("ignore")
del _warnings


def explain(redirect=None):
    """Deprecated: Use explain_traceback() instead.
    """
    # The reason for removing this is to avoid confusion with
    # explain() used in the console.
    session.explain_traceback(redirect=redirect)


def explain_traceback(redirect=None):
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


def get_output(flush=True):
    """Returns the result of captured output as a string which can be
    written anywhere desired.

    By default, flushes all the captured content.
    However, this can be overriden if desired.
    """
    return session.get_captured(flush=flush)


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


def is_installed():
    """Returns True if Friendly-traceback is installed, False otherwise"""
    return session.installed


def uninstall():
    """Resets sys.excepthook to Python's default"""
    session.uninstall()


def run(
    filename,
    lang=None,
    include="friendly_tb",
    args=None,
    console=True,
    use_rich=False,
    theme="dark",
    redirect=None,
):
    """Given a filename (relative or absolute path) ending with the ".py"
    extension, this function uses the
    more complex ``exec_code()`` to run a file.

    If console is set to ``False``, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True`` (the default), the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currenly only ``en`` (default) and ``fr``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised.

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...

    ``use_rich``: set to ``True`` if Rich is available and the environment
    supports it.

    ``theme``: Theme to be used with Rich. Currently only ``dark``,
    the default, and ``light`` are available. ``light`` is meant for
    light coloured background and has not been extensively tested.
    """
    session.install(lang=lang, include=include, redirect=redirect)
    if use_rich:
        if friendly_rich.rich_available:
            session.use_rich = True
            session.set_formatter("rich", theme=theme)

    if args is not None:
        sys.argv = [filename]
        sys.argv.extend(list(args))
    module_globals = editors_helper.exec_code(path=filename, lang=lang, include=include)
    if console:
        start_console(
            local_vars=module_globals,
            use_rich=use_rich,
            banner="",
            theme=theme,
            include=include,
        )
    else:
        return module_globals


def set_formatter(formatter=None, **kwds):
    """Sets the default formatter. If no argument is given, the default
    formatter is used.

    A custom formatter must accept ``info`` as a required arguments
    as well an additional argument whose value is subject to change.
    See formatters.py for details.
    """
    session.set_formatter(formatter=formatter, **kwds)


def show_again():
    """Shows the previously recorded traceback info again, on the default stream.

    Primarily intended to be used when the user changes
    a verbosity level to view the last computed traceback
    in a given language.
    """
    session.show_traceback_info_again()


def start_console(
    local_vars=None,
    use_rich=False,
    include="friendly_tb",
    lang="en",
    banner=None,
    theme="dark",
):
    """Starts a Friendly console"""
    from . import console

    console.start_console(
        local_vars=local_vars,
        use_rich=use_rich,
        include=include,
        lang=lang,
        banner=banner,
        theme=theme,
    )


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


def set_lang(lang):
    """Sets the language to be used by gettext.

    If no translations exist for that language, the original
    English strings will be used.
    """
    session.install_gettext(lang)


def get_lang():
    """Returns the current language that had been set for translations.

    Note that the value returned may not reflect truly what is being
    see by the end user: if the translations do not exist for that language,
    the default English strings are used.
    """
    return session.lang


def set_include(include):
    "placeholder docstring"
    session.set_include(include)


def get_include():
    "placeholder docstring"
    return session.get_include()


def set_stream(redirect=None):
    """Sets the stream to which the output should be directed.

    If the string ``"capture"`` is given as argument, the
    output is saved and can be later retrieved by ``get_output()``.

    If no argument is given, the default stream (stderr) is set.
    """
    session.set_redirect(redirect=redirect)


def get_stream():
    """Returns the value of the current stream used for output."""
    return session.write_err


# -----------------------------------------
#   Deprecated functions
# -----------------------------------------


def set_level(verbosity_level):
    """Deprecated. Details about new API to be provided later."""
    print("friendly-traceback set_level is deprecated; defaults will be used.")
    set_include("explain")
