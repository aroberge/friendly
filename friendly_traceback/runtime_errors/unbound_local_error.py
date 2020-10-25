"""UnboundLocalError cases"""

import re

from ..my_gettext import current_lang
from .. import info_variables


def get_cause(value, info, frame):
    _ = current_lang.translate

    pattern = re.compile(r"local variable '(.*)' referenced before assignment")
    match = re.search(pattern, str(value))
    if match:
        return local_variable_referenced(match.group(1), info, frame)

    return _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def local_variable_referenced(unknown_name, info, frame):
    _ = current_lang.translate

    scopes = info_variables.get_definition_scope(unknown_name, frame)

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
        info["suggest"] = _(
            "Did you forget to add either `global {var_name}` or \n"
            "`nonlocal {var_name}`?\n"
        ).format(var_name=unknown_name)
        return cause

    cause = ""

    if "global" in scopes:
        scope = "global"
    elif "nonlocal" in scopes:
        scope = "nonlocal"

    cause = _(
        "The name `{var_name}` exists in the {scope} scope.\n"
        "Perhaps the statement\n\n"
        "    {scope} {var_name}\n\n"
        "should have been included as the first line inside your function.\n"
    ).format(var_name=unknown_name, scope=scope)

    info["suggest"] = _("Did you forget to add `{scope} {var_name}`?\n").format(
        var_name=unknown_name, scope=scope
    )

    return cause
