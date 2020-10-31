import re

from ..my_gettext import current_lang
from .. import info_variables


def get_cause(value, info, frame):
    _ = current_lang.translate

    pattern = re.compile(r"name '(.*)' is not defined")
    match = re.search(pattern, str(value))
    if not match:
        return

    unknown_name = match.group(1)

    cause = _("In your program, the unknown name is `{var_name}`.\n").format(
        var_name=unknown_name
    )

    hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar_names = info_variables.get_similar_names(unknown_name, frame)
    cause += hint + similar_names

    return cause
