"""info_variables.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""
import ast
import builtins
import sys

from . import utils
from . import debug_helper
from . import token_utils

from .path_info import path_utils
from .my_gettext import current_lang

# third-party
try:
    from asttokens import ASTTokens  # noqa
    from pure_eval import Evaluator, group_expressions  # noqa
except ImportError:
    pass  # ignore errors when processed by Sphinx


INDENT = "        "
MAX_LENGTH = 65


def convert_type(short_form):
    _ = current_lang.translate
    if short_form == "complex":
        return _("a complex number")
    elif short_form == "dict":
        return _("a dictionary (`dict`)")
    elif short_form == "float":
        return _("a number (`float`)")
    elif short_form == "int":
        return _("an integer (`int`)")
    elif short_form == "list":
        return _("a `list`")
    elif short_form == "NoneType":
        return _("a variable equal to `None` (`NoneType`)")
    elif short_form == "set":
        return _("a `set`")
    elif short_form == "str":
        return _("a string (`str`)")
    elif short_form == "tuple":
        return _("a `tuple`")
    elif short_form == "frozenset":
        return _("a `frozenset`")
    else:
        return short_form


# pure_eval is primarily designed to find "interesting" expressions,
# which do not include literals. However, when trying to determine
# the cause of an object, we sometimes might want to find literals
# that are in a given line where an exception is raised.
# For this reason, we monkeypatch pure_eval to add one method
# and one very simple function.


def literal_expressions_grouped(self, root):
    """Find all literal in the given tree parsed by ASTTokens.
    It returns a list of pairs (tuples) containing the text of a node
    that is a literal and its actual value.
    """
    # Except for the inner function is_literal
    # this is modeled after interesting_expressions_grouped
    def is_literal(node, _ignore):
        try:
            return ast.literal_eval(node)
        except ValueError:
            pass

    return group_expressions(
        pair
        for pair in self.find_expressions(root)
        if (
            is_literal(*pair) or is_literal(*pair) in [list(), tuple(), dict(), set([])]
        )
    )


def get_all_objects(line, frame):
    """Given a (partial) line of code and a frame,
    obtains a dict containing all the relevant information about objects
    found on that line so that they can be formatted as part of the
    answer to "where()" or they can be used during the analysis
    of the cause of the exception.

    The dict returned has four keys.
    The first three, 'locals', 'globals', 'nonlocals',
    each containing a list of tuples, each tuple being of the form
    (name, repr(obj), obj) where name --> obj.

    The fourth key, 'literals', contains a list of tuples of the form
    ('name', obj). It is only occasionally used in helping to make
    suggestions regarding the cause of some exception.
    """
    objects = {
        "locals": [],
        "globals": [],
        "literals": [],
        "builtins": [],
        "name, obj": [],
    }

    scopes = (
        ("locals", frame.f_locals),  # always have locals before globals
        ("globals", frame.f_globals),
    )

    names = set([])
    try:
        atok = ASTTokens(line, parse=True)
    except SyntaxError:  # this should not happen
        atok = None

    if atok is not None:
        for scope, scope_dict in scopes:
            for nodes, obj in Evaluator(scope_dict).interesting_expressions_grouped(
                atok.tree
            ):
                name = atok.get_text(nodes[0])
                if name in names:
                    continue
                names.add(name)
                objects[scope].append((name, repr(obj), obj))
                objects["name, obj"].append((name, obj))

        Evaluator.literal_expressions_grouped = literal_expressions_grouped
        for nodes, obj in Evaluator({}).literal_expressions_grouped(atok.tree):  # noqa
            name = atok.get_text(nodes[0])
            objects["literals"].append((name, obj))
            objects["name, obj"].append((name, obj))

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
                    obj = getattr(builtins, name)
                    objects["builtins"].append((name, repr(obj), obj))
                    objects["name, obj"].append((name, obj))

    dotted_names = get_dotted_names(line)
    for name in dotted_names:
        for scope, scope_dict in scopes:
            try:  # TODO: see if pure_eval could not be used instead of eval
                obj = eval(name, scope_dict)
                if (name, obj) not in objects["name, obj"]:
                    objects[scope].append((name, repr(obj), obj))
                    objects["name, obj"].append((name, obj))
            except Exception:
                pass

    # TODO: check to see if this is still needed
    objects["nonlocals"] = get_nonlocal_objects(frame)
    return objects


def get_dotted_names(line):
    """Retrieve dotted names, i.e. something like A.x or A.x.y, etc.

    In principle, pure_eval/ASTTokens used above should be able to
    retrieve dotted names. However, I have not (yet) been able to do so
    without this hack.
    """
    names = []
    prev_token = token_utils.tokenize("")[0]  # convenient guard
    dot_found = False
    tokens = token_utils.get_significant_tokens(line)
    for tok in tokens:
        if tok == ".":
            dot_found = True
            continue
        if tok.is_identifier():
            if prev_token.is_identifier() and dot_found:
                previous_name = names[-1]
                names.append(previous_name + "." + tok.string)
                dot_found = False
                continue
            else:
                names.append(tok.string)
            names.append(tok.string)
        prev_token = tok
        dot_found = False

    # remove duplicate and names without "."
    dotted_names = []
    for name in names:
        if name not in dotted_names and "." in name:
            dotted_names.append(name)
    return dotted_names


def get_nonlocal_objects(frame):
    """Identifies objects found in a nonlocal scope, and return
    a list of tuples of the form (name, repr(obj), obj) for each
    such object found.
    """
    globals_ = frame.f_globals
    non_locals = []
    while frame.f_back is not None:
        frame = frame.f_back
        # By creating a new list here, we prevent a failure when
        # running with pytest.
        for name in list(frame.f_locals):
            if name in globals_ or name in non_locals:
                continue
            obj = frame.f_locals[name]
            non_locals.append((name, repr(obj), obj))
    return non_locals


def get_object_from_name(name, frame):
    """Given the name of an object, for example 'str', or 'A' for
    class A, returns a basic object of that type found in a frame,
    or None.
    """

    # We must guard against people defining their own type with a
    # standard name by checking standard types last.

    if name in frame.f_locals:
        return frame.f_locals[name]
    elif name in frame.f_globals:
        return frame.f_globals[name]
    elif name in dir(builtins):  # Do this last
        return getattr(builtins, name)
    return None


def get_variables_in_frame_by_scope(frame, scope):
    """Returns a list of variables based on the provided scope, which must
    be one of 'local', 'global', or 'nonlocal'.
    """
    if scope == "local":
        return frame.f_locals
    elif scope == "global":
        return frame.f_globals
    elif scope == "nonlocal":
        globals_ = frame.f_globals
        non_locals = {}
        while frame.f_back is not None:
            frame = frame.f_back
            # By creating a new list here, we prevent a failure when
            # running with pytest.
            for key in list(frame.f_locals):
                if key in globals_ or key in non_locals:
                    continue
                non_locals[key] = frame.f_locals[key]
        return non_locals
    else:
        debug_helper.log("Internal error in get_variable_in_frame_by_scope()")
        debug_helper.log(f"unknown scope '{scope}'")
        debug_helper.log_error()
        return {}


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

    for name, value, obj in objects["locals"]:
        result = format_var_info(name, value, obj)
        names_info.append(result)

    for name, value, obj in objects["globals"]:
        result = format_var_info(name, value, obj, "globals")
        names_info.append(result)

    for name, value, obj in objects["builtins"]:
        result = format_var_info(name, value, obj)
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
        file_name, obj_name = name.split(".<locals>.")
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
