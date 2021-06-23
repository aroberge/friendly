"""info_variables.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""
import ast
import builtins
import sys

from . import utils
from . import token_utils

from .path_info import path_utils
from .my_gettext import current_lang

# third-party
try:
    from asttokens import ASTTokens  # noqa
    from pure_eval import Evaluator, group_expressions  # noqa
except ImportError:  # pragma: no cover
    pass  # ignore errors when processed by Sphinx


INDENT = " " * 8
MAX_LENGTH = 65


def convert_type(short_form):
    _ = current_lang.translate

    forms = {
        "complex": _("a complex number"),
        "dict": _("a dictionary (`dict`)"),
        "float": _("a number (`float`)"),
        "frozenset": _("a `frozenset`"),
        "int": _("an integer (`int`)"),
        "list": _("a `list`"),
        "NoneType": _("a variable equal to `None` (`NoneType`)"),
        "set": _("a `set`"),
        "str": _("a string (`str`)"),
        "string": _("a string (`str`)"),
        "tuple": _("a `tuple`"),
    }
    return forms.get(short_form, short_form)


def get_all_objects(line, frame):
    """Given a (partial) line of code and a frame,
    obtains a dict containing all the relevant information about objects
    found on that line so that they can be formatted as part of the
    answer to "where()" or they can be used during the analysis
    of the cause of the exception.

    The dict returned has five keys.
    The first three, 'locals', 'globals', 'builtins',
    each containing a list of tuples, each tuple being of the form
    (name, repr(obj), obj) where name --> obj.

    The fourth key, 'expressions', contains a list of tuples of the form
    ('name', obj). It is only occasionally used in helping to make
    suggestions regarding the cause of some exception.
    """
    objects = {
        "locals": [],
        "globals": [],
        "builtins": [],
        "expressions": [],
        "name, obj": [],
    }

    scopes = (
        ("locals", frame.f_locals),  # always have locals before globals
        ("globals", frame.f_globals),
    )

    names = set()

    tokens = token_utils.get_significant_tokens(line)
    for tok in tokens:
        if tok.is_identifier():
            name = tok.string
            if name in names:
                continue
            for scope, scope_dict in scopes:
                if name in scope_dict:
                    names.add(name)
                    obj = scope_dict[name]
                    objects[scope].append((name, repr(obj), obj))
                    objects["name, obj"].append((name, obj))
                    break
            else:
                if name in dir(builtins):
                    names.add(name)
                    obj = getattr(builtins, name)
                    objects["builtins"].append((name, repr(obj), obj))
                    objects["name, obj"].append((name, obj))

    try:
        atok = ASTTokens(line, parse=True)
    except SyntaxError:  # this should not happen
        return objects

    if atok is not None:
        evaluator = Evaluator.from_frame(frame)
        for nodes, obj in group_expressions(
            pair for pair in evaluator.find_expressions(atok.tree)
        ):
            name = atok.get_text(nodes[0])
            if name in names:
                continue
            names.add(name)
            objects["name, obj"].append((name, obj))
            try:
                # We're not interested in showing literals in the list of variables
                ast.literal_eval(name)
            except Exception:  # noqa
                objects["expressions"].append((name, obj))

    return objects


def get_object_from_name(name, frame):
    """Given the name of an object, for example 'str', or 'A' for
    class A, returns a basic object of that type found in a frame,
    or None.
    """
    # TODO:
    """
    There might be multiple objects with the same name (in different scope)
    in a given frame.  For example:

    class A: pass  # first A
    def f():
       class A: pass   # second A
       return A()
    a = f()
    a.x  # raise AttributeError: 'A' object has no attribute 'x'

    Here, we would identify 'A' as being the first, even though 'a' is an
    instance of the second 'A'.

    This should be tested thoroughly and likely result in a warning given
    about possibly not being able to identify the correct object.
    """
    # We must guard against people defining their own type with a
    # standard name by checking standard types last.
    if name in frame.f_locals:
        return frame.f_locals[name]

    if name in frame.f_globals:
        return frame.f_globals[name]

    if name in dir(builtins):  # Do this last
        return getattr(builtins, name)
    return None


def get_variables_in_frame_by_scope(frame, scope):
    """Returns a list of variables based on the provided scope, which must
    be one of 'local', 'global', or 'nonlocal'.
    """
    if scope == "local":
        return frame.f_locals

    if scope == "global":
        return frame.f_globals

    if scope == "nonlocal":
        non_locals = {}
        while frame.f_back is not None:
            frame = frame.f_back
            # By creating a new list here, we prevent a failure when
            # running with pytest.
            for key in list(frame.f_locals):
                if key in non_locals:
                    continue
                non_locals[key] = frame.f_locals[key]
        return non_locals


def get_definition_scope(variable_name, frame):
    """Returns a list of scopes ('local', 'global', 'nonlocal')
    in which a variable is defined.
    """
    scopes = []
    for scope in ["local", "global", "nonlocal"]:
        in_scope = get_variables_in_frame_by_scope(frame, scope)
        if variable_name in in_scope:
            scopes.append(scope)
    return scopes


def get_var_info(line, frame):
    """Given a frame object, it obtains the value (repr) of the names
    found in the logical line (which may span many lines in the file)
    where the exception occurred.

    We ignore values found *only* in nonlocal scope as they should not
    be relevant.
    """

    names_info = []
    objects = get_all_objects(line.strip(), frame)

    objects["locals"].sort()
    for name, value, obj in objects["locals"]:
        result = format_var_info(name, value, obj)
        names_info.append(result)

    objects["globals"].sort()
    for name, value, obj in objects["globals"]:
        result = format_var_info(name, value, obj, "globals")
        names_info.append(result)

    objects["builtins"].sort()
    for name, value, obj in objects["builtins"]:
        result = format_var_info(name, value, obj)
        names_info.append(result)

    objects["expressions"].sort()
    for name, obj in objects["expressions"]:
        result = format_var_info(name, repr(obj), obj)
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
        path = path_utils.shorten_path(path[:-1])  # -1 removes >
        # Avoid lines that are too long
        if len(obj_repr) + len(path) < MAX_LENGTH:
            name = obj_repr + "> from " + path
        else:
            name = obj_repr + f">\n{INDENT}from " + path
    # The following is done so that, when using rich, pygments
    # does not style the - and 'in' in a weird way.
    name = name.replace("built-in", "builtin")
    if name.startswith("<"):
        name = name.replace("'", "")
    if ".<locals>." in name:
        parts = name.split(".<locals>.")
        file_name = parts[0]
        obj_name = ".".join(parts[1:])
        # file_name, obj_name = name.split(".<locals>.")
        if name.startswith("<function "):
            start = "<function "
        elif name.startswith("<class "):
            start = "<class "
        else:
            start = "<"
        file_name = file_name.replace(start, "")
        name = start + obj_name + " from " + file_name
    if "__main__." in name:
        name = name.replace("__main__.", "") + " from __main__"
    return name


def format_var_info(name, value, obj, _global=""):
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

    result = f"    {_global}{name}:  {value}"
    if length_info:
        _indent = " " * (7 + len(name))
        result += f"\n{_indent}len({name}): {length_info}\n"
    return result


def get_similar_names(name, frame):
    """This function looks for objects with names similar to 'name' in
    either the current locals() and globals() as well as in
    Python's builtins.
    """
    similar = {}
    # We need to first combine the candidates from all possible sources
    # so as to treat them on an equal footing.
    locals_ = list(frame.f_locals.keys())
    globals_ = list(frame.f_globals.keys())
    builtins_ = dir(builtins)
    all_similar = utils.get_similar_words(name, locals_ + globals_ + builtins_)
    similar["locals"] = []
    similar["globals"] = []
    similar["builtins"] = []
    for word in all_similar:
        if word in locals_:
            similar["locals"].append(word)
        elif word in globals_:
            similar["globals"].append(word)
        else:
            similar["builtins"].append(word)
    if all_similar:
        most_similar = utils.get_similar_words(name, all_similar)
        similar["best"] = most_similar[0]
    elif name in ["length", "lenght"]:
        # utils.get_similar_words() used above only look for relatively
        # minor letter mismatches in making suggestions.
        # Here we add a few additional hard-coded cases.
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

    HOWEVER, when an exception is raised, it seems that the only type hints
    that are picked up correctly are those found in the global scope.
    """

    _ = current_lang.translate

    type_hint_found_in_scope = _(
        "A type hint found for `{name}` in the {scope} scope.\n"
        "Perhaps you had used a colon instead of an equal sign and wrote\n\n"
        "    {name} : {hint}\n\n"
        "instead of\n\n"
        "    {name} = {hint}\n"
    )
    nonlocals = get_variables_in_frame_by_scope(frame, "nonlocal")

    scopes = (
        ("local", frame.f_locals),
        ("global", frame.f_globals),
        ("nonlocal", nonlocals),
    )

    for scope, scope_dict in scopes:
        if "__annotations__" in scope_dict and name in scope_dict["__annotations__"]:
            hint = scope_dict["__annotations__"][name]
            # For Python 3.10+, all type hints are strings
            if (
                isinstance(hint, str)
                and sys.version_info.major == 3
                and sys.version_info.minor < 10
            ):
                hint = repr(hint)
            return type_hint_found_in_scope.format(name=name, scope=scope, hint=hint)

    return ""
