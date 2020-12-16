"""Getting specific information for AttributeError"""
import sys

import re

from ..my_gettext import current_lang
from ..utils import get_similar_words, tokenize_source
from ..path_info import path_utils
from . import stdlib_modules


def get_cause(value, frame, tb_data):
    _ = current_lang.translate
    message = str(value)
    cause = hint = None

    pattern1 = re.compile(r"module '(.*)' has no attribute '(.*)'")
    match1 = re.search(pattern1, message)

    pattern2 = re.compile(r"type object '(.*)' has no attribute '(.*)'")
    match2 = re.search(pattern2, message)

    pattern3 = re.compile(r"'(.*)' object has no attribute '(.*)'")
    match3 = re.search(pattern3, message)

    if match1:
        cause, hint = attribute_error_in_module(match1.group(1), match1.group(2), frame)
    elif match2:
        cause, hint = handle_type_object_case(match2.group(1), match2.group(2), frame)
    elif match3:
        if match3.group(1) == "NoneType":
            cause = _(
                "You are attempting to access the attribute `{attr}`\n"
                "for a variable whose value is `None`."
            ).format(attr=match3.group(2))
        else:
            cause, hint = attribute_error_in_object(
                match3.group(1), match3.group(2), tb_data, frame
            )
    return cause, hint


# ======= Attribute error in module =========


def attribute_error_in_module(module, attribute, frame):
    """Attempts to find if a module attribute or module name might have been misspelled"""
    _ = current_lang.translate
    cause = hint = None
    try:
        mod = sys.modules[module]
    except Exception:
        cause = _(
            "This should not happen:\n"
            "Python tells us that module `{module}` does not have an "
            "attribute named `{attribute}`.\n"
            "However, it does not appear that module `{module}` was imported.\n"
        ).format(module=module, attribute=attribute)
        return cause, hint

    similar_attributes = get_similar_words(attribute, dir(mod))
    if similar_attributes:
        if len(similar_attributes) == 1:
            hint = _("Did you mean `{name}`?\n").format(name=similar_attributes[0])
            cause = _(
                "Perhaps you meant to write `{module}.{correct}` "
                "instead of `{module}.{typo}`\n"
            ).format(correct=similar_attributes[0], typo=attribute, module=module)
            return cause, hint
        else:
            # transform ['a', 'b', 'c'] in `"a, b, c"`
            candidates = [
                "{c}".format(c=c.replace("'", "")) for c in similar_attributes
            ]
            candidates = ", ".join(candidates)
            hint = _("Did you mean one of the following: `{names}`?\n").format(
                names=candidates
            )
            cause = _(
                "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
                "the following names which are attributes of module `{module}`:\n"
                "`{candidates}`\n"
            ).format(candidates=candidates, typo=attribute, module=module)
            return cause, hint

    # TODO: check to see if module shadows a standard library module;
    # perhaps use turtle as a good case.

    if module in stdlib_modules.names and hasattr(mod, "__file__"):
        mod_path = path_utils.shorten_path(mod.__file__)
        if not mod_path.startswith("PYTHON_LIB:"):
            hint = _("Did you give your program the same name as a Python module?")
            cause = _(
                "You imported a module named `{module}` from `{mod_path}`.\n"
                "There is also a module named `{module}` in Python's standard library.\n"
                "Perhaps you need to rename your module.\n"
            ).format(module=module, mod_path=mod_path)
            return cause, hint

    # the following is untested
    # We look for another module currently known for which such an attribute exists.
    relevant_modules = []
    for mod_name in sys.modules:
        if mod_name in frame.f_globals or mod_name in frame.f_locals:
            relevant_modules.append((mod_name, mod))

    for mod_name, mod in relevant_modules:
        # TODO: consider the case where more than one module could be
        # meant
        if attribute in dir(mod):
            hint = _("Did you mean `{name}`?\n").format(name=mod_name)
            cause = _(
                "Perhaps you meant to use the attribute `{attribute}` of \n"
                "module `{mod_name}` instead of module `{module}`.\n"
            ).format(attribute=attribute, mod_name=mod_name, module=module)
            return cause, hint

    cause = _(
        "Python tells us that no object with name `{attribute}` is\n"
        "found in module `{module}`.\n"
    ).format(attribute=attribute, module=module)
    return cause, hint


# ======= Handle type error case =========


def handle_type_object_case(obj_type, attribute, frame):
    _ = current_lang.translate
    cause = hint = None

    if obj_type in frame.f_locals:
        obj = frame.f_locals[obj_type]
        known_attributes = dir(obj)
    elif obj_type in frame.f_globals:
        obj = frame.f_globals[obj_type]
        known_attributes = dir(obj)
    else:
        obj = None
        if attribute in frame.f_locals:
            obj = frame.f_locals[attribute]
        elif attribute in frame.f_globals:
            obj = frame.f_globals[attribute]
        else:
            return cause, hint
        hint = _("Did you use a period instead of a comma?")
        cause = _(
            "`{attribute}` is a known object,"
            " and is not an attribute of objects of type `{obj_type}`.\n"
            "Perhaps you wrote a period where you meant to write a comma.\n"
        ).format(attribute=attribute, obj_type=obj_type)

    similar = get_similar_words(attribute, known_attributes)
    if similar:
        cause, hint = handle_attribute_typo_for_type(obj_type, attribute, similar)
    else:
        # All we can do is rephrase the message, so that it can also
        # be translated.
        cause = _(
            "The object of type `{obj_type}` has no attribute named `{attribute}`."
        ).format(obj_type=obj_type, attribute=attribute)
    return cause, hint


def handle_attribute_typo_for_type(obj_type, attribute, similar):
    """Takes care of misspelling of existing attribute of object of a given type,
    whose name could not be identified."""
    _ = current_lang.translate

    cause = hint = None
    if len(similar) == 1:
        hint = _("Did you mean `{name}`?\n").format(name=similar[0])
        cause = _(
            "You wrote `{attribute}` which is not a valid attribute"
            " for objects of type `{obj_type}`\n"
            "However, objects of type `{obj_type}` have an attribute named `{correct}`"
            "which is similar to what you wrote.\n"
        ).format(correct=similar[0], typo=attribute, obj_type=obj_type)
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
        candidates = ", ".join(candidates)
        hint = _("Did you mean one of the following: `{name}`?\n").format(
            name=candidates
        )
        cause = _(
            "You wrote `{attribute}` which is not a valid attribute"
            " for objects of type `{obj_type}`\n"
            "However, objects of type `{obj_type}` have have the following attributes"
            "which are similar to what you wrote:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, attribute=attribute, obj_type=obj_type)
    return cause, hint


# ======= Handle attribute error in object =========


def attribute_error_in_object(obj_type, attribute, tb_data, frame):
    """Attempts to find if object attribute might have been misspelled"""
    _ = current_lang.translate
    cause = hint = None
    standard_types = {
        "bool": bool,
        "dict": dict,
        "list": list,
        "set": set,
        "str": str,
        "tuple": tuple,
    }

    if obj_type in standard_types:
        obj = standard_types[obj_type]
        known_attributes = dir(obj)
    elif obj_type in frame.f_locals:
        obj = frame.f_locals[obj_type]
        known_attributes = dir(obj)
    elif obj_type in frame.f_globals:
        obj = frame.f_globals[obj_type]
        known_attributes = dir(obj)
    else:
        return cause, hint

    # The error message gives us the type of object instead of the true object
    # name. Depending on whether or not we can identify the true object name,
    # we might need to change slightly the feedback with give.
    found_name = True
    true_name, index = find_true_object_name_and_position(
        obj, obj_type, attribute, tb_data, frame
    )
    if true_name != obj_type:
        found_name = False

    similar = get_similar_words(attribute, known_attributes)
    if similar:
        return handle_attribute_typo_for_object(true_name, attribute, similar)

    known_builtin = perhaps_builtin(attribute, known_attributes)
    if known_builtin:
        return use_builtin_function(true_name, attribute, known_builtin)

    if not found_name:
        # We have identified the first object; is the attribute a second object
        if attribute in frame.f_globals or attribute in frame.f_locals:
            cause, hint = missing_comma(true_name, attribute)
            return cause, hint

    if found_name:
        cause = _(
            "The object of type `{obj}` has no attribute named `{attr}`.\n"
        ).format(obj=obj_type, attr=attribute)
    else:
        cause = _("The object `{obj}` has no attribute named `{attr}`.\n").format(
            obj=true_name, attr=attribute
        )
    known_attributes = [a for a in known_attributes if "__" not in a]
    if len(known_attributes) > 10:
        known_attributes = known_attributes[:9] + ["..."]
    if known_attributes:
        cause += _(
            "The following are some of its known attributes:\n" "`{names}`."
        ).format(names=", ".join(known_attributes))
    return cause, hint


def handle_attribute_typo_for_object(obj_name, attribute, similar):
    """Takes care of misspelling of existing attribute of object whose
       name could be identified.
    """
    _ = current_lang.translate

    if len(similar) == 1:
        hint = _("Did you mean `{name}`?\n").format(name=similar[0])
        cause = _(
            "Perhaps you meant to write `{obj}.{correct}` "
            "instead of `{obj}.{typo}`\n"
        ).format(correct=similar[0], typo=attribute, obj=obj_name)
    else:
        # transform ['a', 'b', 'c'] in "[`a`, `b`, `c`]"
        candidates = ["{c}".format(c=c.replace("'", "")) for c in similar]
        candidates = ", ".join(candidates)
        hint = _("Did you mean one of the following: `{name}`?\n").format(
            name=candidates
        )
        cause = _(
            "Instead of writing `{obj}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of object `{obj}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=attribute, obj=obj_name)
    return cause, hint


def perhaps_builtin(attribute, known_attributes):
    if attribute in ["min", "max"]:
        return attribute
    if attribute in ["len", "length"] and "__len__" in known_attributes:
        return "len"


def use_builtin_function(obj_name, attribute, known_builtin):
    _ = current_lang.translate
    hint = _("Did you mean to use `{known_builtin}({obj_name})`?").format(
        known_builtin=known_builtin, obj_name=obj_name
    )
    cause = _(
        "The object `{obj_name}` has no attribute named `{attribute}`.\n"
        "Perhaps you can use the Python builtin function `{known_builtin}` instead:\n"
        "`{known_builtin}({obj_name})`."
    ).format(known_builtin=known_builtin, obj_name=obj_name, attribute=attribute)
    return cause, hint


def find_true_object_name_and_position(obj, obj_name, attribute, tb_data, frame):

    tokens = tokenize_source(tb_data.bad_line)
    for index, tok in enumerate(tokens):
        try:
            candidate = eval(tok.string, frame.f_globals, frame.f_locals)
            if (
                isinstance(candidate, obj)
                and tokens[index + 1] == "."
                and tokens[index + 2] == attribute
            ):
                return tok.string, index
        except Exception:
            pass

    return obj_name, None


def missing_comma(first, second):
    _ = current_lang.translate

    hint = _("Did you mean to separate object names by a comma?")

    cause = _(
        "`{second}` is not an attribute of `{first}`.\n"
        "However, both `{first}` and `{second}` are known objects.\n"
        "Perhaps you wrote a period to separate these two objects, \n"
        "instead of using a comma.\n"
    ).format(first=first, second=second)

    return cause, hint
