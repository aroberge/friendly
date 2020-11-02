"""info_variables.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""
import builtins

from . import utils
from .my_gettext import current_lang
from .friendly_exception import FriendlyException

INDENT = "        "
MAX_LENGTH = 65


def get_variables_in_frame_by_scope(frame, scope):
    """Returns a list of variables based on the provided scope, which must
    be one of 'local', 'global', or 'nonlocal'.
    """
    if scope == "local":
        return frame.f_locals
    elif scope == "global":
        return frame.f_globals
    elif scope == "declared nonlocal":
        return list(frame.f_code.co_freevars)
    elif scope == "nonlocal":
        globals_ = frame.f_globals
        nonlocals_ = {}
        while frame.f_back is not None:
            frame = frame.f_back
            # By creating a new list here, we prevent a failure when
            # running with pytest.
            for key in list(frame.f_locals):
                if key in globals_ or key in nonlocals_:
                    continue
                nonlocals_[key] = frame.f_locals[key]
        return nonlocals_
    else:
        raise FriendlyException(
            "Internal error: unknown scope '{scope}' "
            + "in get_variable_in_frame_by_scope()."
        )


def get_definition_scope(variable_name, frame):
    """Returns a list of scopes ('local', 'global', 'nonlocal',
    'declared nonlocal') in which a variable is defined.
    """
    scopes = []
    for scope in ["local", "global", "nonlocal", "declared nonlocal"]:
        in_scope = get_variables_in_frame_by_scope(frame, scope)
        if variable_name in in_scope:
            scopes.append(scope)
    return scopes


def get_var_info(displayed_source, frame):
    """Given a frame object, it obtains the value (repr) of the names
    found in the logical line (which may span many lines in the file)
    where the exception occurred.

    We ignore values found *only* in nonlocal scope as they should not
    be relevant.

    We also only show the variables that appeared in the partial source
    displayed, which looks something like this::

           1: def test():
           2:    a = b = 2
        -->3:    c = a + b + d
           4:
    """
    loc = frame.f_locals
    glob = frame.f_globals
    names_info = []

    lines = displayed_source.split("\n")
    names = []
    for line in lines:
        line = ":".join(line.split(":")[1:]).strip()
        tokens = utils.tokenize_source(line)
        for tok in tokens:
            if tok.is_identifier():
                if tok.string not in names:
                    names.append(tok.string)

    for name in names:
        result = ""
        if name in loc:
            result = format_var_info(name, loc)
        elif name in glob:
            result = format_var_info(name, glob, _global=True)
        elif name in dir(builtins):
            result = format_var_info(name, builtins, _builtins=True)
        if result:
            names_info.append(result)

    if names_info:
        names_info.append("")
    return "\n".join(names_info)


def simplify_name(name):
    """Remove irrelevant memory location information from functions, etc."""
    # There are two reasons to do this:
    # 1. this information is essentially of no value for beginners
    # 2. Removing this information ensures that consecutive runs of
    #    script to create tracebacks for the documentation will yield
    #    exactly the same results. This makes it easier to spot changes/regressions.
    if " at " in name:
        name = name.split(" at ")[0] + ">"
    elif " from " in name:  # example: module X from stdlib_path
        obj_repr, path = name.split(" from ")
        path = utils.shorten_path(path[:-1])  # -1 removes >
        # Avoid lines that are too long
        if len(obj_repr) + len(path) < MAX_LENGTH:
            name = obj_repr + "> from " + path
        else:
            name = obj_repr + f">\n{INDENT}from " + path
    # The following is done so that, when using rich, pygments
    # does not style the - and 'in' in a weird way.
    name = name.replace("built-in", "builtin")
    return name.replace("<__main__.", "<")


def format_var_info(name, _dict, _global="", _builtins=""):
    """Formats the variable information so that it fits on a single line
    for each variable.

    The format we want is something like the following:

    [global] name: repr(name)

    However, if repr(name) exceeds a certain value, it is truncated.
    When that is the case, if len(name) is defined, as is the case for
    lists, tuples, dicts, etc., then len(name) is shown on a separate line.
    This can be useful information in case of IndexError and possibly
    others.
    """
    _ = current_lang.translate
    length_info = ""
    if _global:
        _global = "global "

    if _builtins:
        obj = getattr(_dict, name)
    else:
        obj = _dict[name]
    try:
        value = repr(obj)
    except Exception:
        return ""

    if value.startswith("<") and value.endswith(">"):
        value = simplify_name(value)

    if len(value) > MAX_LENGTH and not value.startswith("<"):
        # We reduce the length of the repr, indicate this by ..., but we
        # also keep the last character so that the repr of a list still
        # ends with ], that of a tuple still ends with ), etc.
        if "," in value:  # try to truncate at a natural place
            parts = value.split(", ")
            length = 0
            new_parts = []
            for part in parts:
                if len(part) + length > MAX_LENGTH:
                    break
                new_parts.append(part + ", ")
                length += len(part) + 2
            if new_parts:
                value = "".join(new_parts) + "..." + value[-1]
            else:
                value = value[0 : MAX_LENGTH - 5] + "..." + value[-1]
        else:
            value = value[0 : MAX_LENGTH - 5] + "..." + value[-1]
        try:
            length_info = len(obj)
        except TypeError:
            pass

    result = f"    {_global}{name}: {value}"
    if length_info:
        result += f"\n{INDENT}len({name}): {length_info}"
    return result


def get_similar_names(name, frame):
    """This function looks for objects with names similar to 'name' in
    either the current locals() and globals() as well as in
    Python's builtins.
    """
    similar = {}
    locals_ = get_variables_in_frame_by_scope(frame, "local")
    similar["locals"] = utils.get_similar_words(name, locals_)

    globals_ = get_variables_in_frame_by_scope(frame, "global")
    names = utils.get_similar_words(name, globals_)
    similar["globals"] = [name for name in names if name not in similar["locals"]]

    similar["builtins"] = utils.get_similar_words(name, dir(builtins))
    all_similar = similar["locals"] + similar["globals"] + similar["builtins"]
    if all_similar:
        most_similar = utils.get_similar_words(name, all_similar)
        similar["best"] = most_similar[0]
    else:
        # utils.get_similar_words() used above only look for relatively
        # minor letter mismatches in making suggestions.
        # Here we add a few additional hard-coded cases.
        if name in ["length", "lenght"]:
            similar["builtins"] = ["len"]
            similar["best"] = "len"
        else:
            similar["best"] = None
    return similar


def name_has_type_hint(name, frame):
    """Identifies if a variable name has a type hint associated with it.

    This can be useful if a user write something like::

        name : something
        use(name)

    instead of::

        name = something
        use(name)

    and sees a NameError.

    Note that this is a draft implementation that only looks in the
    local and global scope, and ignore nonlocal scope(s).
    """

    _ = current_lang.translate

    type_hint_found_in_scope = _(
        "A type hint found for `{name}` in the {scope} scope.\n"
    )
    perhaps = _(
        "Perhaps you had used a colon instead of an equal sign and written\n\n"
        "    {name} : {hint}\n\n"
        "instead of\n\n"
        "    {name} = {hint}\n"
    )

    scopes = (("local", frame.f_locals), ("global", frame.f_globals))

    for scope, scope_dict in scopes:
        if "__annotations__" in scope_dict and name in scope_dict["__annotations__"]:
            hint = scope_dict["__annotations__"][name]
            if isinstance(hint, str):
                hint = f"'{hint}'"
            message = type_hint_found_in_scope.format(name=name, scope=scope)
            message += perhaps.format(name=name, hint=hint)
            return message

    return ""
