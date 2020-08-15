"""The functions in this module have been created so that user of tools,
like the editor Mu, could use Friendly-traceback.

See https://aroberge.github.io/friendly-traceback-docs/docs/html/mu.html
for an example.

At the moment, only run() is part of the public API.
"""
# TODO: update docstring when documentation is revised to include info
# about this module.
import sys

from .core import explain_traceback
from .source_cache import cache
from .my_gettext import current_lang
from .session import session
from .console import start_console


def advanced_check_syntax(
    *, source=None, filename="Fake filename", path=None, verbosity=None, lang=None
):
    """This uses Python's ``compile()`` builtin which does some analysis of
       its code argument and will raise an exception if it identifies
       some syntax errors, but also some less common "overflow" and "value"
       errors.

       Compared with ``check_syntax()``, the prefix ``advanced_`` simply refers
       to the greater number of arguments, which are specified as
       keywords-only arguments.

       This function can either be used on a file, using the ``path`` argument, or
       on some code passed as a string, using the ``source`` argument.
       For the latter case, one can also specify a corresponding ``filename``:
       this could be useful if this function is invoked from a GUI-based
       editor.

       Note that the ``path`` argument, if provided, takes precedence
       over the ``source`` argument.

       Two additional named arguments, ``verbosity`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.

       Returns a tuple containing a code object and a filename if no exception
       has been raised, False otherwise.

    """
    _ = current_lang.translate

    saved_except_hook, saved_verbosity = _save_settings()
    saved_lang = _temp_set_lang(lang)

    if path is not None:
        try:
            with open(path, encoding="utf8") as f:
                source = f.read()
                filename = path
        except Exception:
            # Do not show the Python traceback which would include
            #  the call to open() in the traceback
            if verbosity is None:
                session.set_verbosity(5)
            else:
                session.set_verbosity(verbosity)
            explain_traceback()
            _reset(saved_except_hook, saved_lang, saved_verbosity)
            return False

    cache.add(filename, source)
    try:
        code = compile(source, filename, "exec")
    except Exception:
        if verbosity is None:
            session.set_verbosity(1)  # our default
        else:
            session.set_verbosity(verbosity)
        explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_verbosity)
        return False

    _reset(saved_except_hook, saved_lang, saved_verbosity)
    return code


def check_syntax(filename, lang=None):
    """Given a filename (relative or absolute path), this function calls the
       more keyword-based advanced_check_syntax(),
       and will raise an exception if it identifies
       some syntax errors, but also some less common "overflow" and "value"
       errors.  advanced_check_syntax() provides a more flexibility

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.

       Returns False if problems have been found, None otherwise.
       """
    if advanced_check_syntax(path=filename, lang=lang):
        return None
    else:
        return False


def exec_code(*, source=None, path=None, verbosity=None, lang=None):
    """This uses check_syntax to see if the code is valid and, if so,
       executes it into a globals dict containing only
       ``{"__name__": "__main__"}``.
       If no SyntaxError exception is raised, this dict is returned;
       otherwise, an empty dict is returned.

       It can either be used on a file, using the ``path`` argument, or
       on some code passed as a string, using the ``source`` argument.

       Note that the ``path`` argument, if provided, takes precedence
       over the ``source`` argument.

       Two additional named arguments, ``verbosity`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.
    """
    code = advanced_check_syntax(
        source=source, path=path, verbosity=verbosity, lang=lang
    )
    if not code:
        return {}

    saved_except_hook, saved_verbosity = _save_settings()
    saved_lang = _temp_set_lang(lang)

    module_globals = {"__name__": "__main__"}
    try:
        exec(code, module_globals)
    except Exception:
        if verbosity is None:
            session.set_verbosity(1)  # our default
        else:
            session.set_verbosity(verbosity)
        explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_verbosity)
        return module_globals

    _reset(saved_except_hook, saved_lang, saved_verbosity)
    return module_globals


def run(filename, lang=None, verbosity=1, args=None, console=False):
    """Given a filename (relative or absolute path), this function uses the
       more complex exec_code() to run a file.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call. By default, it uses the value of 1 for
       the verbosity level.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.

       Returns an empty dict if a SyntaxError was raised,
       otherwise returns the dict in which the module (filename) was executed.
       """
    if args is not None:
        sys.argv = [filename]
        args = [arg.strip() for arg in args.split(" ")]
        # TODO: add extensive tests for this
        sys.argv.extend([arg for arg in args if arg])  # remove empty strings
    module_globals = exec_code(path=filename, lang=lang, verbosity=verbosity)
    if console:
        start_console(local_vars=module_globals)
    else:
        return module_globals


def _temp_set_lang(lang):
    """If lang is not none, temporarily set session.lang to the provided
       value. Keep track of the original lang setting and return it.

       A value of None for saved_lang indicates that no resetting will
       be required.
       """
    saved_lang = None
    if lang is not None:
        saved_lang = session.lang
        if saved_lang != lang:
            session.install_gettext(lang)
        else:
            saved_lang = None
    return saved_lang


def _save_settings():
    current_except_hook = sys.excepthook
    current_verbosity = session.level

    return current_except_hook, current_verbosity


def _reset(saved_except_hook, saved_lang, saved_verbosity):
    """Resets both verbosity and lang to their original values"""
    if saved_lang is not None:
        session.install_gettext(saved_lang)
    session.set_verbosity(saved_verbosity)
    # set_verbosity(0) restores sys.excepthook to sys.__excepthook__
    # which might not be what is wanted. So, we reset sys.excepthook last
    sys.excepthook = saved_except_hook
