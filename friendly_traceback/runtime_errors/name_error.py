import re

from ..my_gettext import current_lang, no_information, internal_error
from .. import info_variables
from .. import debug_helper
from .. import token_utils


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:
        debug_helper.log_error(e)
        return {"cause": internal_error(), "suggest": internal_error()}


def _get_cause(value, frame, tb_data):

    name, fn = get_unknown_name(str(value))
    if name is not None:
        return fn(name, frame, tb_data)

    return {"cause": no_information()}


def get_unknown_name(message):
    """Retrieves the value of the unknown name from a message and identifies
    which function must be called for further processing.

    Note that this function is also used in core.py, for a different purpose.
    """
    pattern = re.compile(r"name '(.*)' is not defined")
    match = re.search(pattern, message)
    if match:
        return match.group(1), name_not_defined

    pattern2 = re.compile(
        r"free variable '(.*)' referenced before assignment in enclosing scope"
    )
    match = re.search(pattern2, message)
    if match:
        return match.group(1), free_variable_referenced

    return None, None


def free_variable_referenced(unknown_name, *_args):
    _ = current_lang.translate
    cause = _(
        "In your program, `{var_name}` is an unknown name\n"
        "that had been declared as belonging in a nonlocal scope;\n"
        "however, no such name could not be found.\n"
    ).format(var_name=unknown_name)
    return {"cause": cause}


def name_not_defined(unknown_name, frame, tb_data):
    _ = current_lang.translate
    cause = _("In your program, `{var_name}` is an unknown name.\n").format(
        var_name=unknown_name
    )
    if unknown_name in ["i", "j"]:
        hint = _("Did you mean `1j`?\n")
        cause += _(
            "However, sometimes `{name}` is intended to represent\n"
            "the square root of `-1` which is written as `1j` in Python.\n"
        ).format(name=unknown_name)
        return {"cause": cause, "suggest": hint}

    type_hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar = info_variables.get_similar_names(unknown_name, frame)
    if similar["best"] is not None:
        hint = _("Did you mean `{name}`?\n").format(name=similar["best"])
    elif type_hint:
        hint = _("Did you use a colon instead of an equal sign?\n")
    else:
        hint = None

    additional = type_hint + format_similar_names(unknown_name, similar)
    try:
        more, hint = missing_self(unknown_name, frame, tb_data, hint)
        additional += more
    except Exception as e:
        print("exception raised: ", e)
    if not additional:
        additional = _("I have no additional information for you.\n")

    cause = {"cause": cause + additional}
    if hint is None:
        return cause
    cause["suggest"] = hint
    return cause


def format_similar_names(name, similar):
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


def missing_self(unknown_name, frame, tb_data, hint):
    """If the unknown name is referred to with no '.' before it,
    and is an attribute of a known object, perhaps 'self.'
    is missing."""
    _ = current_lang.translate
    message = ""
    try:
        tokens = token_utils.get_significant_tokens(tb_data.bad_line)
    except Exception:
        return message, hint

    if not tokens:
        return message, hint

    prev_token = tokens[0]
    for token in tokens:
        if token == unknown_name and prev_token != ".":
            break
        prev_token = token
    else:
        return message, hint

    env = (("local", frame.f_locals), ("global", frame.f_globals))

    for scope, dict_ in env:
        names = info_variables.get_variables_in_frame_by_scope(frame, scope)
        dict_copy = dict(dict_)
        for name in names:
            if name in dict_copy:
                obj = dict_copy[name]
                known_attributes = dir(obj)
                if unknown_name in known_attributes:
                    suggest = _("Did you forget to add `self`?")
                    if hint is None:
                        hint = suggest
                    else:
                        hint += " " + suggest
                    message = _(
                        "The {scope} object `{obj}`"
                        " has an attribute named `{unknown_name}`.\n"
                        "Perhaps you should have written `self.{unknown_name}`"
                        " instead of `{unknown_name}`.\n"
                    ).format(
                        scope=scope,
                        obj=info_variables.simplify_name(repr(obj)),
                        unknown_name=unknown_name,
                    )
                    return message, hint

    return message, hint
