"""Getting specific information for ImportError"""

import re
import sys

from ..my_gettext import current_lang
from ..utils import get_similar_words


def get_cause(value, info, frame):
    _ = current_lang.translate

    message = str(value)

    # Python 3.7+
    pattern2 = re.compile(r"cannot import name '(.*)' from '(.*)'")
    match = re.search(pattern2, message)
    if match:
        return cannot_import_name_from(match.group(1), match.group(2), info, frame)

    # Python 3.6
    pattern3 = re.compile(r"cannot import name '(.*)'")
    match = re.search(pattern3, message)
    if match:
        return cannot_import_name(match.group(1), info, frame)

    return _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def cannot_import_name_from(name, module, info, frame):
    _ = current_lang.translate

    cause = _(
        "The object that could not be imported is `{name}`.\n"
        "The module or package where it was \n"
        "expected to be found is `{module}`.\n"
    ).format(name=name, module=module)

    try:
        mod = sys.modules[module]
    except Exception:
        return cause
    similar = get_similar_words(name, dir(mod))
    if not similar:
        return cause

    if len(similar) == 1:
        info["suggest"] = _("Did you mean `{name}`?\n").format(name=similar[0])
        return _(
            "Perhaps you meant to import `{correct}` from `{module}` "
            "instead of `{typo}`\n"
        ).format(correct=similar[0], typo=name, module=module)
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
        candidates = ", ".join(candidates)
        info["suggest"] = _("Did you mean one of the following: `{names}`?\n").format(
            names=candidates
        )
        return _(
            "Instead of trying to import `{typo}` from `{module}`, \n"
            "perhaps you meant to import one of \n"
            "the following names which are found in module `{module}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=name, module=module)

    return _(
        "The object that could not be imported is `{name}`.\n"
        "The module or package where it was \n"
        "expected to be found is `{module}`.\n"
    ).format(name=name, module=module)


def cannot_import_name(name, info, frame):
    # Python 3.6 does not give us the name of the module
    _ = current_lang.translate
    pattern = re.compile(r"from (.*) import")
    if "badline" in info:
        match = re.search(pattern, info["badline"])
        if match:
            return cannot_import_name_from(name, match.group(1), info, frame)

    return _("The object that could not be imported is `{name}`.\n").format(name=name)
