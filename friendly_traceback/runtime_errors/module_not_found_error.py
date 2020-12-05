"""Getting specific information for ModuleNotFoundError"""

import re

from ..my_gettext import current_lang
from ..utils import get_similar_words

from . import stdlib_modules

# TODO: case to consider

#     import os.pathh
# ModuleNotFoundError: No module named 'os.pathh'; 'os' is not a package


def get_cause(value, info, frame):
    _ = current_lang.translate

    message = str(value)

    cause = _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )
    hint = None  # unused for now

    pattern = re.compile(r"No module named '(.*)'")
    match = re.search(pattern, message)
    if match:
        cause, hint = no_module_named(match.group(1))
        if hint:
            info["suggest"] = hint
    return cause


def no_module_named(name):
    _ = current_lang.translate
    similar = get_similar_words(name, stdlib_modules.names)

    hint = None
    cause = _(
        "The name of the module that could not be imported is `{name}`.\n"
    ).format(name=name)
    if not similar:
        return cause, hint

    hint = _("Did you mean `{name}`?\n").format(name=similar[0])

    if len(similar) > 1:
        cause += _(
            "The following existing modules have names that are similar \n"
            "to the module you tried to import: `{names}`\n"
        ).format(names=", ".join(similar))
    else:
        cause += _("`{name}` is an existing module that has a similar name.\n").format(
            name=similar[0]
        )

    return cause, hint
