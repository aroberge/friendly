"""Getting specific information for AttributeError"""

import sys

import re

from ..my_gettext import current_lang
from ..utils import get_similar_words, tokenize_source


def get_cause(value, info, frame):
    _ = current_lang.translate
    message = str(value)

    pattern = re.compile(r"module '(.*)' has no attribute '(.*)'")
    match = re.search(pattern, message)
    if match:
        return attribute_error_in_module(match.group(1), match.group(2), info)

    pattern2 = re.compile(r"type object '(.*)' has no attribute '(.*)'")
    match = re.search(pattern2, message)
    if match:
        return attribute_error_in_object(match.group(1), match.group(2), info, frame)

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
                match.group(1), match.group(2), info, frame
            )


def attribute_error_in_module(module, attribute, info):
    """Attempts to find if a module attribute might have been misspelled"""
    _ = current_lang.translate
    try:
        mod = sys.modules[module]
    except Exception:
        return False
    similar = get_similar_words(attribute, dir(mod))
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
        info["suggest"] = _("Did you mean one of the following: `{names}`?\n").format(
            names=candidates
        )
        return _(
            "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of module `{module}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=attribute, module=module)


def attribute_error_in_object(obj_name, attribute, info, frame):
    """Attempts to find if object attribute might have been misspelled"""
    _ = current_lang.translate

    try:
        obj = eval(obj_name, frame.f_globals, frame.f_locals)
        known_attributes = dir(obj)
    except Exception:
        return False

    # The error message gives us the type of object instead of the true object
    # name. Depending on whether or not we can identify the true object name,
    # we might need to change slightly the feedback with give.
    obj_of_type = True
    true_name = find_true_object_name(obj, obj_name, attribute, info, frame)
    if true_name != obj_name:
        obj_of_type = False

    similar = get_similar_words(attribute, known_attributes)
    if similar:
        return handle_typo(true_name, attribute, similar, info)

    known_builtin = identify_builtin(attribute, known_attributes)
    if known_builtin:
        return use_builtin_function(true_name, attribute, known_builtin, info)

    if obj_of_type:
        explain = _(
            "The object of type `{obj}` has no attribute named `{attr}`.\n"
        ).format(obj=obj_name, attr=attribute)
    else:
        explain = _("The object `{obj}` has no attribute named `{attr}`.\n").format(
            obj=true_name, attr=attribute
        )
    known_attributes = [a for a in known_attributes if "__" not in a]
    if known_attributes:
        explain += _(
            "The following are some of its known attributes:\n" "`{names}`."
        ).format(names=", ".join(known_attributes))
    return explain


def handle_typo(obj_name, attribute, similar, info):
    """Takes care of misspelling of existing attribute of object"""
    _ = current_lang.translate

    if len(similar) == 1:
        info["suggest"] = _("Did you mean `{name}`?\n").format(name=similar[0])
        return _(
            "Perhaps you meant to write `{obj}.{correct}` "
            "instead of `{obj}.{typo}`\n"
        ).format(correct=similar[0], typo=attribute, obj=obj_name)
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
        candidates = ", ".join(candidates)
        info["suggest"] = _("Did you mean one of the following: `{name}`?\n").format(
            name=candidates
        )
        return _(
            "Instead of writing `{obj}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of object `{obj}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=attribute, obj=obj_name)


def identify_builtin(attribute, known_attributes):
    if attribute in ["min", "max"]:
        return attribute
    if attribute in ["len", "length"] and "__len__" in known_attributes:
        return "len"


def use_builtin_function(obj_name, attribute, known_builtin, info):
    _ = current_lang.translate
    info["suggest"] = _("Did you mean to use `{known_builtin}({obj_name})`?").format(
        known_builtin=known_builtin, obj_name=obj_name
    )
    return _(
        "The object `{obj_name}` has no attribute named `{attribute}`.\n"
        "Perhaps you can use the Python builtin function `{known_builtin}` instead:\n"
        "`{known_builtin}({obj_name})`."
    ).format(known_builtin=known_builtin, obj_name=obj_name, attribute=attribute)


def find_true_object_name(obj, obj_name, attribute, info, frame):

    if "badline" not in info:
        return obj_name
    tokens = tokenize_source(info["badline"])
    for index, tok in enumerate(tokens):
        try:
            candidate = eval(tok.string, frame.f_globals, frame.f_locals)

            # There could be more than one object of the same type on the
            # line of code identified as problematic. We need to ensure that
            # we have the correct one.
            if (
                isinstance(candidate, obj)
                and tokens[index + 1].string == "."
                and tokens[index + 2].string == attribute
            ):
                return tok.string
        except Exception:
            pass

    return obj_name
