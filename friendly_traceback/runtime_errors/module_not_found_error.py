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

    pattern = re.compile(r"No module named '(.*)'")
    match = re.search(pattern, message)
    if match:
        return no_module_named(match.group(1), info)

    return _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def no_module_named(name, info):
    _ = current_lang.translate
    similar = get_similar_words(name, stdlib_modules.names)

    explain = _(
        "The name of the module that could not be imported is `{name}`.\n"
    ).format(name=name)
    if not similar:
        return explain

    info["suggest"] = _("Did you mean `{name}`?\n").format(name=similar[0])

    if len(similar) > 1:
        explain += _(
            "The following existing modules have names that are similar \n"
            "to the module you tried to import: `{names}`\n"
        ).format(names=", ".join(similar))
    else:
        explain += _(
            "`{name}` is an existing module that has a similar name.\n"
        ).format(name=similar[0])

    return explain
