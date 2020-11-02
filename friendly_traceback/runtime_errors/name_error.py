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
    if hint:
        return cause + hint
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

    elif nb_similar_names == 1:
        if similar["locals"]:
            return (
                _("The similar name `{name}` was found in the local scope. ").format(
                    name=str(similar["locals"][0]).replace("'", "")
                )
                + "\n"
            )
        elif similar["globals"]:
            similar_name = similar["globals"][0]
            if name != similar_name:
                return (
                    _(
                        "The similar name `{name}` was found in the global scope. "
                    ).format(name=similar_name.replace("'", ""))
                    + "\n"
                )
            else:
                return (
                    _("The name `{name}` was found in the global scope. ").format(
                        name=name
                    )
                    + "\n"
                )
        else:
            return (
                _("The Python builtin `{name}` has a similar name. ").format(
                    name=str(similar["builtins"][0]).replace("'", "")
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
