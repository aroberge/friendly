import re

from ..my_gettext import current_lang
from .. import info_variables
from .. import utils


def get_cause(value, info, frame):
    _ = current_lang.translate

    message = str(value)

    pattern = re.compile(r"name '(.*)' is not defined")
    match = re.search(pattern, message)
    if match:
        return name_not_defined(match.group(1), info, frame)

    pattern2 = re.compile(
        r"free variable '(.*)' referenced before assignment in enclosing scope"
    )
    match = re.search(pattern2, message)
    if match:
        return free_variable_referenced(match.group(1), info, frame)

    return _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def free_variable_referenced(unknown_name, info, frame):
    _ = current_lang.translate
    cause = _(
        "In your program, `{var_name}` is an unknown name\n"
        " but has been found to appear in a nonlocal scope where "
        "it had not been assigned a value.\n"
    ).format(var_name=unknown_name)
    hint = info_variables.name_has_type_hint(unknown_name, frame)
    if hint:  # TODO: I don't think this can ever find anything when an exception
        return cause + hint  # is raised; I need to check this.
    else:
        return cause + _("I have no additional information for you.")


def name_not_defined(unknown_name, info, frame):
    _ = current_lang.translate
    cause = _("In your program, `{var_name}` is an unknown name.\n").format(
        var_name=unknown_name
    )

    hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar = info_variables.get_similar_names(unknown_name, frame)
    if similar["best"] is not None:
        info["suggest"] = _("Did you mean `{name}`?").format(name=similar["best"])
    elif hint:
        info["suggest"] = _("Did you use a colon instead of an equal sign?")

    additional = hint + format_similar_names(unknown_name, similar, hint)
    try:
        additional += missing_self(unknown_name, frame, info)
    except Exception as e:
        print("exception raised: ", e)
    if not additional:
        additional = _("I have no additional information for you.")
    return cause + additional


def format_similar_names(name, similar, hint):
    """This function formats the names that were found to be similar"""
    _ = current_lang.translate

    nb_similar_names = (
        len(similar["locals"]) + len(similar["globals"]) + len(similar["builtins"])
    )
    if nb_similar_names == 0:
        return ""

    found_local = _("The similar name `{name}` was found in the local scope.\n")
    found_global = _("The similar name `{name}` was found in the global scope.\n")
    name_found = _("The name `{name}` was found in the global scope.\n")
    builtin_similar = _("The Python builtin `{name}` has a similar name.\n")

    if nb_similar_names == 1:
        if similar["locals"]:
            name = str(similar["locals"][0]).replace("'", "")
            return found_local.format(name=name)
        elif similar["globals"]:
            similar_name = similar["globals"][0]
            if name != similar_name:
                name = similar_name.replace("'", "")
                return found_global.format(name=name)
            else:
                return name_found.format(name=name)
        else:
            return builtin_similar.format(name=name)

    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=name)

    for scope, pre in (
        ("locals", _("*   Local scope: ")),
        ("globals", _("*   Global scope: ")),
        ("builtins", _("*   Python builtins: ")),
    ):
        if similar[scope]:
            message += pre + str(similar[scope])[1:-1].replace("'", "`") + "\n"

    return message


def missing_self(unknown_name, frame, info):
    """If the unknown name is referred to with no '.' before it,
    and is an attribute of a known object, perhaps 'self.'
    is missing."""
    _ = current_lang.translate

    try:
        tokens = utils.get_significant_tokens(info["bad_line"])
    except Exception:
        return ""

    if not tokens:
        return ""

    prev_token = tokens[0]
    for token in tokens:
        if token == unknown_name and prev_token != ".":
            break
        prev_token = token
    else:
        return ""

    env = (("local", frame.f_locals), ("global", frame.f_globals))

    for scope, dict_ in env:
        names = info_variables.get_variables_in_frame_by_scope(frame, scope)
        dict_copy = dict(dict_)
        for name in names:
            try:
                obj = eval(name, dict_copy)  # Can raise SyntaxError and possibly others
                known_attributes = dir(obj)
                if unknown_name in known_attributes:
                    suggest = _("Did you forget to add `self`?")
                    if "suggest" not in info:
                        info["suggest"] = suggest
                    else:
                        info["suggest"] += " " + suggest
                    return _(
                        "The {scope} object `{obj}`"
                        " has an attribute named `{unknown_name}`.\n"
                        "Perhaps you should have written `self.{unknown_name}`"
                        " instead of `{unknown_name}`.\n"
                    ).format(
                        scope=scope,
                        obj=info_variables.simplify_name(repr(obj)),
                        unknown_name=unknown_name,
                    )
            except Exception:
                pass

    return ""
