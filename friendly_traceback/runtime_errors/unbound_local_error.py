import re

from ..my_gettext import current_lang
from .. import info_variables


def get_cause(value, info, frame):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # local variable 'a' referenced before assignment

    pattern = re.compile(r"local variable '(.*)' referenced before assignment")
    match = re.search(pattern, str(value))
    if match is None:
        return _(
            "No information is known about this exception.\n"
            "Please report this example to\n"
            "https://github.com/aroberge/friendly-traceback/issues\n"
        )
    unknown_name = match.group(1)

    scopes = info_variables.get_definition_scope(unknown_name, frame)

    if "global" in scopes:
        cause = _(
            "The variable that appears to cause the problem is `{var_name}`.\n"
            "Perhaps the statement\n\n"
            "    global {var_name}\n\n"
            "should have been included as the first line inside your function.\n"
        ).format(var_name=unknown_name)

        info["suggest"] = _("Did you forget to add `global {var_name}`?\n").format(
            var_name=unknown_name
        )

    hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar_names = info_variables.get_similar_var_names(unknown_name, frame)
    cause += hint + similar_names
    return cause
