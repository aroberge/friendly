import sys

import re

from ..my_gettext import current_lang
from ..utils import edit_distance


def get_cause(value, info, frame):
    # str(value) is expected to be something like
    #
    # "AttributeError: type object 'A' has no attribute 'x'"
    _ = current_lang.translate
    message = str(value)

    pattern = re.compile(r"module '(.*)' has no attribute '(.*)'")
    match = re.search(pattern, message)
    if match:
        return attribute_error_in_module(message, match.group(1), match.group(2), info)

    pattern2 = re.compile(r"type object '(.*)' has no attribute '(.*)'")
    match = re.search(pattern2, message)
    if match:
        return _(
            "You are attempting to access the attribute `{attr}`\n"
            "for an object of type `{obj}`."
        ).format(obj=match.group(1), attr=match.group(2))

    pattern3 = re.compile(r"'(.*)' object has no attribute '(.*)'")
    match = re.search(pattern3, message)
    if match:
        if match.group(1) == "NoneType":
            return _(
                "You are attempting to access the attribute `{attr}`\n"
                "for a variable whose value is `None`."
            ).format(attr=match.group(2))
        else:
            return attribute_error_in_object(
                message, match.group(1), match.group(2), info, frame
            )

    return


def attribute_error_in_module(message, module, attribute, info):
    """Attempts to find if a module attribute might have been misspelled"""
    _ = current_lang.translate
    try:
        mod = sys.modules[module]
    except Exception:
        return False
    similar = edit_distance(attribute, dir(mod))
    if not similar:
        return False

    if len(similar) == 1:
        info["suggest"] = _("Did you mean `{name}`?\n").format(name=similar[0])
        return _(
            "Perhaps you meant to write `{module}.{correct}` "
            "instead of `{module}.{typo}`\n"
        ).format(correct=similar[0], typo=attribute, module=module)
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
        candidates = ", ".join(candidates)
        info["suggest"] = _("Did you mean one of the following: `{name}`?\n").format(
            name=candidates
        )
        return _(
            "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of module `{module}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=attribute, module=module)


def attribute_error_in_object(message, obj_name, attribute, info, frame):
    """Attempts to find if object attribute might have been misspelled"""
    _ = current_lang.translate
    # try:
    #     mod = sys.modules[module]
    # except Exception:
    #     return False
    # similar = edit_distance(attribute, dir(mod))
    # if not similar:
    #     return False

    # if len(similar) == 1:
    #     info["suggest"] = _("Did you mean `{name}`?\n").format(name=similar[0])
    #     return _(
    #         "Perhaps you meant to write `{module}.{correct}` "
    #         "instead of `{module}.{typo}`\n"
    #     ).format(correct=similar[0], typo=attribute, module=module)
    # else:
    #     # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
    #     candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
    #     candidates = ", ".join(candidates)
    #     info["suggest"] = _("Did you mean one of the following: `{name}`?\n").format(
    #         name=candidates
    #     )
    #     return _(
    #         "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
    #         "the following names which are attributes of module `{module}`:\n"
    #         "`{candidates}`\n"
    #     ).format(candidates=candidates, typo=attribute, module=module)

    return _(
        "In your program, the object is `{obj}` and the attribute is `{attr}`.\n"
    ).format(obj=obj_name, attr=attribute)
