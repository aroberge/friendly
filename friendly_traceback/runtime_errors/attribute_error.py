import sys

from ..my_gettext import current_lang
from ..utils import edit_distance


def process_error(etype, value, info, frame):
    # str(value) is expected to be something like
    #
    # "AttributeError: type object 'A' has no attribute 'x'"
    _ = current_lang.translate
    message = str(value)
    ignore, obj, ignore, attribute, ignore = message.split("'")
    if message.startswith("module "):
        cause_identified = attribute_error_in_module(message, obj, attribute)
        if cause_identified:
            return cause_identified
    elif message.startswith("'NoneType'"):
        return _(
            "You are attempting to access the attriburte `{attr}`\n"
            "for a variable whose value is `None`."
        ).format(attr=attribute)
    return _(
        "In your program, the object is `{obj}` and the attribute is `{attr}`.\n"
    ).format(obj=obj, attr=attribute)


def attribute_error_in_module(message, module, attribute):
    """Attempts to find if a module attribute might have been misspelled"""
    _ = current_lang.translate
    try:
        mod = sys.modules[module]
    except Exception:
        return False
    misspelled = edit_distance(attribute, dir(mod))
    if not misspelled:
        return False

    if len(misspelled) == 1:
        return _("Perhaps you meant to write `{correct}` instead of `{typo}`\n").format(
            correct=misspelled[0], typo=attribute
        )
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = str(["`{c}`".format(c=c) for c in misspelled])
        candidates = candidates.replace("'", "")
        return _(
            "Instead of writing `{typo}`, perhaps you meant one of the following:\n"
            "{candidates}\n"
        ).format(candidates=candidates, typo=attribute)
