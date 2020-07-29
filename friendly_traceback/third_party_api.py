"""The functions in this module have been created so that user of tools,
like the editor Mu, could use Friendly-traceback.

See https://aroberge.github.io/friendly-traceback-docs/docs/html/mu.html
for an example.

Note that most tools can be written so as to make direct use of the
standard API.
"""
import sys

from .core import explain_traceback
from .source_cache import cache
from .my_gettext import current_lang
from .session import session


def advanced_check_syntax(
    *, source=None, filename="Fake filename", path=None, level=None, lang=None
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

       Two additional named arguments, ``level`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.

       Returns a tuple containing a code object and a filename if no exception
       has been raised, False otherwise.

    """
    _ = current_lang.translate

    saved_except_hook, saved_level = _save_settings()
    saved_lang = _temp_set_lang(lang)

    if path is not None:
        try:
            with open(path, encoding="utf8") as f:
                source = f.read()
                filename = path
        except Exception:
            # Do not show the Python traceback which would include
            #  the call to open() in the traceback
            if level is None:
                session.set_level(5)
            else:
                session.set_level(level)
            explain_traceback()
            _reset(saved_except_hook, saved_lang, saved_level)
            return False

    cache.add(filename, source)
    try:
        code = compile(source, filename, "exec")
    except Exception:
        if level is None:
            session.set_level(1)  # our default
        else:
            session.set_level(level)
        explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_level)
        return False

    _reset(saved_except_hook, saved_lang, saved_level)
    return code, filename


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


def exec_code(
    *, source=None, filename="Fake filename", path=None, level=None, lang=None
):
    """This uses check_syntax to see if the code is valid and, if so,
       executes it into an empty dict as globals. If no exception is
       raised, this dict is returned. If an exception is raised, False
       is returned.

       It can either be used on a file, using the ``path`` argument, or
       on some code passed as a string, using the ``source`` argument.
       For the latter case, one can also specify a corresponding ``filename``:
       this could be useful if this function is invoked from a GUI-based
       editor.

       Note that the ``path`` argument, if provided, takes precedence
       over the ``source`` argument.

       Two additional named arguments, ``level`` and ``lang``, can be
       provided to temporarily set the values to be used during this function
       call. The original values are restored at the end.

       If friendly-traceback exception hook has not been set up prior
       to calling check_syntax, it will only be used for the duration
       of this function call.
    """
    result = advanced_check_syntax(
        source=source, filename=filename, path=path, level=level, lang=lang
    )
    if not result:
        return False

    saved_except_hook, saved_level = _save_settings()
    saved_lang = _temp_set_lang(lang)

    my_globals = {}
    code = result[0]

    try:
        exec(code, my_globals)
    except Exception:
        if level is None:
            session.set_level(1)  # our default
        else:
            session.set_level(level)
        explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_level)
        return False

    _reset(saved_except_hook, saved_lang, saved_level)
    return my_globals


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
    current_level = session.level

    return current_except_hook, current_level


def _reset(saved_except_hook, saved_lang, saved_level):
    """Resets both level and lang to their original values"""
    if saved_lang is not None:
        session.install_gettext(saved_lang)
    session.set_level(saved_level)
    # set_level(0) restores sys.excepthook to sys.__excepthook__
    # which might not be what is wanted. So, we reset sys.excepthook last
    sys.excepthook = saved_except_hook
