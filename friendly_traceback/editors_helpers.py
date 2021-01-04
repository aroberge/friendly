"""
editors_helpers.py
------------------

The functions in this module have been created so that user editors/IDEs
could use Friendly-traceback without having to change the content of
their own programs.

None of these are part of the public API.

If you make use of any other function here, please file an issue so
it can be determined if it should be added to the public API.
"""
import sys

from .source_cache import cache
from .my_gettext import current_lang
from .config import session


def check_syntax(
    *, source=None, filename="Fake filename", path=None, include=None, lang=None
):
    """This uses Python's ``compile()`` builtin which does some analysis of
    its code argument and will raise an exception if it identifies
    some syntax errors, but also some less common "overflow" and "value"
    errors.

    Note that there are a few syntax errors that are not caught by this,
    as they are identified by Python very late in its execution
    process. See for example
    `this blog post <https://aroberge.blogspot.com/2019/12/a-tiny-python-exception-oddity.html>`_

    This function can either be used on a file, using the ``path`` argument, or
    on some code passed as a string, using the ``source`` argument.
    For the latter case, one can also specify a corresponding ``filename``:
    this could be useful if this function is invoked from a GUI-based
    editor.

    Note that the ``path`` argument, if provided, takes precedence
    over the ``source`` argument.

    Two additional named arguments, ``include`` and ``lang``, can be
    provided to temporarily set the values to be used during this function
    call. The original values are restored at the end.

    If friendly-traceback exception hook has not been set up prior
    to calling check_syntax, it will only be used for the duration
    of this function call.

    Returns a tuple containing a code object and a filename if no exception
    has been raised, False otherwise.

    """
    _ = current_lang.translate

    saved_except_hook, saved_include = _save_settings()
    saved_lang = _temp_set_lang(lang)

    if path is not None:
        try:
            with open(path, encoding="utf8") as f:
                source = f.read()
                filename = path
        except Exception:
            print("Exception caught")
            # Do not show the Python traceback which would include
            #  the call to open() in the traceback
            if include is None:
                session.set_include("no_tb")
            else:
                session.set_include(include)
            session.explain_traceback()
            _reset(saved_except_hook, saved_lang, saved_include)
            return False

    cache.add(filename, source)
    try:
        code = compile(source, filename, "exec")
    except Exception:
        if include is None:
            session.set_include("explain")  # our default
        else:
            session.set_include(include)
        session.explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_include)
        return ""

    _reset(saved_except_hook, saved_lang, saved_include)
    return code


def exec_code(*, source=None, path=None, include=None, lang=None):
    """This uses check_syntax to see if the code is valid and, if so,
    executes it into a globals dict containing only
    ``{"__name__": "__main__"}``.
    If no ``SyntaxError`` exception is raised, this dict is returned;
    otherwise, an empty dict is returned.

    It can either be used on a file, using the ``path`` argument, or
    on some code passed as a string, using the ``source`` argument.

    Note that the ``path`` argument, if provided, takes precedence
    over the ``source`` argument.

    Two additional named arguments, ``include`` and ``lang``, can be
    provided to temporarily set the values to be used during this function
    call. The original values are restored at the end.

    If friendly-traceback exception hook has not been set up prior
    to calling check_syntax, it will only be used for the duration
    of this function call.
    """
    code = check_syntax(source=source, path=path, include=include, lang=lang)
    if not code:
        return {}

    saved_except_hook, saved_include = _save_settings()
    saved_lang = _temp_set_lang(lang)

    module_globals = {"__name__": "__main__"}
    try:
        exec(code, module_globals)
    except Exception:
        if include is None:
            session.set_include("explain")  # our default
        else:
            session.set_include(include)
        session.explain_traceback()
        _reset(saved_except_hook, saved_lang, saved_include)
        return module_globals

    _reset(saved_except_hook, saved_lang, saved_include)
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
    current_include = session.include

    return current_except_hook, current_include


def _reset(saved_except_hook, saved_lang, saved_include):
    """Resets both include and lang to their original values"""
    if saved_lang is not None:
        session.install_gettext(saved_lang)
    session.set_include(saved_include)
    # set_include(0) restores sys.excepthook to sys.__excepthook__
    # which might not be what is wanted. So, we reset sys.excepthook last
    sys.excepthook = saved_except_hook
