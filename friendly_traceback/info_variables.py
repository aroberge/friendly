"""info_variables.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""
import builtins
import tokenize

from . import utils
from .my_gettext import current_lang


def get_var_info(line, frame):
    """Given a line of code and a frame object, it obtains the
       value (repr) of the names found in either the local or global scope.
    """
    tokens = utils.tokenize_source(line)
    loc = frame.f_locals
    glob = frame.f_globals
    names_info = []
    names = []
    for tok in tokens:
        if tok.type == tokenize.NAME:
            name = tok.string
            if name in names or name in ["True", "False", "None"]:
                continue
            names.append(name)
            result = ""
            if name in loc:
                result = format_var_info(tok, loc)
            elif name in glob:
                result = format_var_info(tok, glob, _global=True)
            elif name in dir(builtins):
                result = format_var_info(tok, builtins, _builtins=True)
            if result:
                names_info.append(result)

    if names_info:
        names_info.append("")
    return "\n".join(names_info)


def format_var_info(tok, _dict, _global="", _builtins=""):
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
    MAX_LENGTH = 65
    length_info = ""
    if _global:
        _global = "global "
    name = tok.string

    if _builtins:
        obj = getattr(_dict, name)
    else:
        obj = _dict[name]
    try:
        value = repr(obj)
    except Exception:
        return ""

    # Remove irrelevant memory location information from functions, etc.
    # There are two reasons to do this:
    # 1. this information is essentially of no value for beginners
    # 2. Removing this information ensures that consecutive runs of
    #    script to create tracebacks for the documentation will yield
    #    exactly the same results. This makes it easier to spot changes/regressions.
    if value.startswith("<") and value.endswith(">"):
        if " at " in value:
            value = value.split(" at ")[0] + ">"
        elif " from " in value:  # example: module X from stdlib_path
            parts = value.split(" from ")
            path = parts[1][:-1].replace("'", "").replace("\\\\", "\\")
            value = parts[0] + "> from " + utils.shorten_path(path)

    if len(value) > MAX_LENGTH:  # too much text would be shown
        # We reduce the length of the repr, indicate this by ..., but we
        # also keep the last character so that the repr of a list still
        # ends with ], that of a tuple still ends with ), etc.
        value = value[0 : MAX_LENGTH - 5] + "..." + value[-1]
        try:
            length_info = len(obj)
        except TypeError:
            pass

    result = f"    {_global}{name}: {value}"
    if length_info:
        result += f"  | len({name}): {length_info}"
    return result


def get_similar_var_names(name, frame):
    """This function looks for object with names similar to 'name' in
       either the current locals() and globals() as well as in
       Python's builtins.
    """
    _ = current_lang.translate
    similar = {}
    similar["locals"] = utils.edit_distance(name, frame.f_locals)
    _globals = utils.edit_distance(name, frame.f_globals)
    similar["globals"] = [var for var in _globals if var not in similar["locals"]]
    similar["builtins"] = utils.edit_distance(name, dir(builtins))

    nb_similar_names = (
        len(similar["locals"]) + len(similar["globals"]) + len(similar["builtins"])
    )
    if nb_similar_names == 0:
        return ""

    elif nb_similar_names == 1:
        if similar["locals"]:
            return (
                _("The similar name `{name}` was found in the local scope. ").format(
                    name=str(similar["locals"][0]).replace("'", "`")
                )
                + "\n"
            )
        elif similar["globals"]:
            return (
                _("The similar name `{name}` was found in the local scope. ").format(
                    name=str(similar["globals"][0]).replace("'", "`")
                )
                + "\n"
            )
        else:
            return (
                _("The Python builtin `{name}` has a similar name. ").format(
                    name=str(similar["builtins"][0]).replace("'", "`")
                )
                + "\n"
            )

    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=name)
    if similar["locals"]:
        message += (
            _("*   Local scope: ")
            + str(similar["locals"])[1:-1].replace("'", "`")
            + "\n"
        )
    if similar["globals"]:
        message += (
            _("*   Global scope: ")
            + str(similar["globals"])[1:-1].replace("'", "`")
            + "\n"
        )
    if similar["builtins"]:
        message += (
            _("*   Python builtins: ")
            + str(similar["builtins"])[1:-1].replace("'", "`")
            + "\n"
        )
    return message


def name_has_type_hint(name, frame):
    """Identifies if a variable name has a type hint associated with it.

        This can be useful if a user write something like::

            name : something
            use(name)

        instead of::

            name = something
            use(name)

        and sees a NameError.
    """

    _ = current_lang.translate

    loc = frame.f_locals
    glob = frame.f_globals

    if "__annotations__" in loc:
        if name in loc["__annotations__"]:
            hint = loc["__annotations__"][name]
            if isinstance(hint, str):
                hint = f"'{hint}'"
            message = _("A type hint found for `{name}` in the local scope.\n").format(
                name=name
            )
            message += _(
                "Perhaps you had written `{name} : {hint}` instead of `{name} = {hint}`.\n"
            ).format(name=name, hint=hint)
            return message

    if "__annotations__" in glob:
        if name in glob["__annotations__"]:
            hint = glob["__annotations__"][name]
            if isinstance(hint, str):
                hint = f"'{hint}'"
            message = _("A type hint found for `{name}` in the global scope.\n").format(
                name=name
            )
            message += _(
                "Perhaps you had written `{name} : {hint}` instead of `{name} = {hint}`.\n"
            ).format(name=name, hint=hint)
            return message
    return ""
