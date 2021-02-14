"""UnboundLocalError cases"""

import re

from ..my_gettext import current_lang, no_information
from .. import info_variables
from .. import debug_helper


def get_cause(value, frame, _tb_data):
    try:
        return _get_cause(value, frame)
    except Exception as e:
        debug_helper.log_error(e)
        return {}


def _get_cause(value, frame):
    _ = current_lang.translate
    cause = {"cause": no_information()}

    pattern = re.compile(r"local variable '(.*)' referenced before assignment")
    match = re.search(pattern, str(value))
    if match:
        cause = local_variable_referenced(match.group(1), frame)

    return cause


def local_variable_referenced(unknown_name, frame):
    _ = current_lang.translate
    scopes = info_variables.get_definition_scope(unknown_name, frame)
    if not scopes:
        similar = info_variables.get_similar_names(unknown_name, frame)
        if similar["best"] is not None:
            best_guess = similar["best"]
            if best_guess in similar["locals"]:
                hint = _("Did you mean `{name}`?\n").format(name=similar["best"])
                cause = format_similar_names(unknown_name, similar)
                return {"cause": cause, "suggest": hint}

        else:
            cause = info_variables.name_has_type_hint(unknown_name, frame)
            if cause:
                hint = _("Did you use a colon instead of an equal sign?\n")
                return {"cause": cause, "suggest": hint}
            else:
                return {}

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
    else:
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
