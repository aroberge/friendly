"""UnboundLocalError cases"""

import re

from ..my_gettext import current_lang, no_information
from .. import info_variables
from .. import debug_helper


def get_cause(value, frame, _tb_data):
    try:
        return _get_cause(value, frame)
    except Exception as e:  # pragma: no cover
        debug_helper.log_error(e)
        return {}


def _get_cause(value, frame):
    _ = current_lang.translate

    pattern = re.compile(r"local variable '(.*)' referenced before assignment")
    match = re.search(pattern, str(value))
    if match:
        cause = local_variable_referenced(match.group(1), frame)
    else:
        cause = {"cause": no_information()}

    return cause


def local_variable_referenced(unknown_name, frame):
    _ = current_lang.translate
    scopes = info_variables.get_definition_scope(unknown_name, frame)
    if not scopes:
        similar = info_variables.get_similar_names(unknown_name, frame)
        all_similar_locals = similar["locals"]
        if all_similar_locals:
            similar_locals = []
            for name in all_similar_locals:
                obj = info_variables.get_object_from_name(name, frame)
                # Usually, this error message will be because we have
                # something like:
                # unknown += ...
                # or equivalent. We make sure to not include similar
                # names that refer to functions, etc., which could
                # not be assigned a value.
                if hasattr(obj, "__add__"):
                    similar_locals.append(name)
            if similar_locals:
                first_guess = similar_locals[0]
                hint = _("Did you mean `{name}`?\n").format(name=first_guess)
                cause = format_similar_names(unknown_name, similar)
                return {"cause": cause, "suggest": hint}

    if "global" in scopes and "nonlocal" in scopes:
        cause = _(
            "The name `{var_name}` exists in both the global and nonlocal scope.\n"
            "This can be rather confusing and is not recommended.\n"
            "Depending on which variable you wanted to refer to, you needed to add either\n\n"
            "    global {var_name}\n\n"
            "or\n\n"
            "    nonlocal {var_name}\n\n"
            "as the first line inside your function.\n"
        ).format(var_name=unknown_name)
        hint = _(
            "Did you forget to add either `global {var_name}` or \n"
            "`nonlocal {var_name}`?\n"
        ).format(var_name=unknown_name)
        return {"cause": cause, "suggest": hint}

    if "global" in scopes:
        scope = "global"
    elif "nonlocal" in scopes:
        scope = "nonlocal"
    else:  # pragma: no cover
        debug_helper.log("problem in local_variable_referenced().")
        debug_helper.log("We have found variables in scopes")
        debug_helper.log("yet not in global nor nonlocal.")
        return {}

    cause = _(
        "The name `{var_name}` exists in the {scope} scope.\n"
        "Perhaps the statement\n\n"
        "    {scope} {var_name}\n\n"
        "should have been included as the first line inside your function.\n"
    ).format(var_name=unknown_name, scope=scope)
    hint = _("Did you forget to add `{scope} {var_name}`?\n").format(
        var_name=unknown_name, scope=scope
    )
    return {"cause": cause, "suggest": hint}


def format_similar_names(unknown_name, similar):
    """This function formats the names that were found to be similar"""
    _ = current_lang.translate

    nb_similar_names = len(similar["locals"])
    if nb_similar_names == 1:
        return (
            _("The similar name `{name}` was found in the local scope. ").format(
                name=str(similar["locals"][0]).replace("'", "")
            )
            + "\n"
        )

    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=unknown_name)
    message += (
        _("*   Local scope: ") + str(similar["locals"])[1:-1].replace("'", "`") + "\n"
    )

    return message
