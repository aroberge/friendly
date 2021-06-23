import re

from ..my_gettext import current_lang, no_information, internal_error
from . import stdlib_modules
from .. import info_variables
from .. import debug_helper
from .. import token_utils


def using_python():  # pragma: no cover
    _ = current_lang.translate
    return _("You are already using Python!")


# The following is also intended to be used in custom environments;
# we currently use it in Mu.  It is meant to recognize names that
# are intended as a single word command, or call to a function
# that does is not available in a given environment.
CUSTOM_NAMES = {}
CUSTOM_NAMES["python"] = using_python
CUSTOM_NAMES["python3"] = using_python


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:  # pragma: no cover
        debug_helper.log_error(e)
        return {"cause": internal_error(), "suggest": internal_error()}


def _get_cause(value, frame, tb_data):

    # We use a different approach in this module than the usual
    # way to loop over the messages, adding message parsers
    # for each case. This is because we need to access get_unknown_name
    # from elsewhere.
    name, fn = get_unknown_name(str(value))
    if name is not None:
        return fn(name, frame, tb_data)

    return {"cause": no_information()}  # pragma: no cover


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

    return None, None  # pragma: no cover


def free_variable_referenced(unknown_name, *_args):
    _ = current_lang.translate
    cause = _(
        "In your program, `{var_name}` is an unknown name\n"
        "that exists in an enclosing scope,\n"
        "but has not yet been assigned a value.\n"
    ).format(var_name=unknown_name)
    return {"cause": cause}


def name_not_defined(unknown_name, frame, tb_data):
    _ = current_lang.translate
    cause = _("In your program, no object with the name `{var_name}` exists.\n").format(
        var_name=unknown_name
    )

    if unknown_name == "ꓺ":  # pragma: no cover
        return flipfloperator()

    known = is_stdlib_module(unknown_name, tb_data)
    if known:
        return known

    if unknown_name in CUSTOM_NAMES:
        bad_line = tb_data.bad_line.replace("(", "").replace(")", "").strip()
        if bad_line == unknown_name:
            cause = CUSTOM_NAMES[unknown_name]()
            return {"cause": cause, "suggest": cause}

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
    except Exception as e:  # pragma: no cover
        debug_helper.log("Problem in name_not_defined()")
        debug_helper.log_error(e)
    if not additional:
        additional = _("I have no additional information for you.\n")

    cause = {"cause": cause + additional}
    if hint is None:
        return cause
    cause["suggest"] = hint
    return cause


def flipfloperator():  # pragma: no cover
    _ = current_lang.translate
    hint = _("You must be a fan of PyConAu!\n")
    cause = _(
        "I am guessing that you tried to use (one of) the flipfloperators\n"
        "shown during the second Lightning Talk session of PyConAu 2018,\n"
        "but that you forgot to import the module from PyPI.\n\n"
        "#### Note that it is still a bad idea.\n"
    )
    return {"cause": cause, "suggest": hint}


def is_stdlib_module(name, tb_data):
    """Determine if an unknown name is to be found in the Python standard library.
    We're looking for something like name.attribute ... with the exception of
    'Turtle' which might be used in Turtle() ..."""
    _ = current_lang.translate
    if name != "Turtle":  # Turtle is a special case
        try:
            tokens = token_utils.get_significant_tokens(tb_data.bad_line)
        except Exception:  # noqa  # pragma: no cover
            debug_helper.log(
                "Problem in getting significant tokens " "in is_stdlib_module()"
            )
            return {}

        prev = "0"
        for tok in tokens:
            if tok == "." and prev == name:
                break
            prev = tok
        else:
            return {}

    # Some Python 2 libraries used names with uppercase letters.
    lowercase = name.lower()
    if name in stdlib_modules.names or lowercase in stdlib_modules.names:
        hint = _("Did you forget to import `{name}`?\n").format(name=lowercase)
        cause = _(
            "The name `{name}` is not defined in your program.\n"
            "Perhaps you forgot to import `{lowercase}` which is found\n"
            "in Python's standard library.\n"
        ).format(name=name, lowercase=lowercase)
        if name != lowercase:
            cause += _(
                "Note that the name of the module is `{lowercase}` and not `{name}`.\n"
            ).format(lowercase=lowercase, name=name)
        return {"cause": cause, "suggest": hint}
    return {}


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
    # name_found = _("The name `{name}` was found in the global scope.\n")
    builtin_similar = _("The Python builtin `{name}` has a similar name.\n")

    if nb_similar_names == 1:
        if similar["locals"]:
            return found_local.format(name=similar["locals"][0])
        if similar["globals"]:
            return found_global.format(name=similar["globals"][0])
        return builtin_similar.format(name=similar["builtins"][0])

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
    # TODO: revise this when looking at https://github.com/aroberge/friendly/issues/202
    message = ""
    try:
        tokens = token_utils.get_significant_tokens(tb_data.bad_line)
    except Exception:  # noqa  # pragma: no cover
        debug_helper.log(
            "Exception raised in missing_self() while trying to get tokens"
        )
        return message, hint

    if not tokens:  # pragma: no cover
        debug_helper.log("No significant token found in missing_self()")
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
