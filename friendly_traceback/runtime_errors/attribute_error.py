"""Getting specific information for AttributeError"""
import builtins
import re
import sys


from ..my_gettext import current_lang, no_information, internal_error
from ..utils import get_similar_words, list_to_string
from ..path_info import path_utils
from .. import info_variables
from .. import debug_helper
from . import stdlib_modules


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception:
        debug_helper.log_error()
        return None, None


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate
    message = str(value)

    pattern1 = re.compile(r"module '(.*)' has no attribute '(.*)'")
    match1 = re.search(pattern1, message)

    pattern2 = re.compile(r"type object '(.*)' has no attribute '(.*)'")
    match2 = re.search(pattern2, message)

    pattern3 = re.compile(r"'(.*)' object has no attribute '(.*)'")
    match3 = re.search(pattern3, message)

    if match1:
        return attribute_error_in_module(match1.group(1), match1.group(2), frame)
    elif match2:
        return attribute_error_in_object(
            match2.group(1), match2.group(2), tb_data, frame
        )
    elif match3:
        if match3.group(1) == "NoneType":
            return {
                "cause": _(
                    "You are attempting to access the attribute `{attr}`\n"
                    "for a variable whose value is `None`."
                ).format(attr=match3.group(2))
            }
        else:
            return attribute_error_in_object(
                match3.group(1), match3.group(2), tb_data, frame
            )
    else:
        return {"cause": no_information()}


# ======= Attribute error in module =========


def attribute_error_in_module(module, attribute, frame):
    """Attempts to find if a module attribute or module name might have been misspelled"""
    _ = current_lang.translate
    try:
        mod = sys.modules[module]
    except Exception:
        cause = _(
            "This should not happen:\n"
            "Python tells us that module `{module}` does not have an "
            "attribute named `{attribute}`.\n"
            "However, it does not appear that module `{module}` was imported.\n"
        ).format(module=module, attribute=attribute)
        return {"cause": cause}

    similar_attributes = get_similar_words(attribute, dir(mod))
    if similar_attributes:
        if len(similar_attributes) == 1:
            hint = _("Did you mean `{name}`?\n").format(name=similar_attributes[0])
            cause = _(
                "Perhaps you meant to write `{module}.{correct}` "
                "instead of `{module}.{typo}`\n"
            ).format(correct=similar_attributes[0], typo=attribute, module=module)
            return {"cause": cause, "suggest": hint}
        else:
            names = list_to_string(similar_attributes)
            hint = _("Did you mean one of the following: `{names}`?\n").format(
                names=names
            )
            cause = _(
                "Instead of writing `{module}.{typo}`, perhaps you meant to write one of \n"
                "the following names which are attributes of module `{module}`:\n"
                "`{names}`\n"
            ).format(names=names, typo=attribute, module=module)
            return {"cause": cause, "suggest": hint}

    if module in stdlib_modules.names and hasattr(mod, "__file__"):
        mod_path = path_utils.shorten_path(mod.__file__)
        if not mod_path.startswith("PYTHON_LIB:"):
            hint = _("Did you give your program the same name as a Python module?\n")
            cause = _(
                "You imported a module named `{module}` from `{mod_path}`.\n"
                "There is also a module named `{module}` in Python's standard library.\n"
                "Perhaps you need to rename your module.\n"
            ).format(module=module, mod_path=mod_path)
            return {"cause": cause, "suggest": hint}

    # TODO: test this
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
            return {"cause": cause, "suggest": hint}

    cause = _(
        "Python tells us that no object with name `{attribute}` is\n"
        "found in module `{module}`.\n"
    ).format(attribute=attribute, module=module)
    return {"cause": cause}


# ======= Handle attribute error in object =========


def attribute_error_in_object(obj_type, attribute, tb_data, frame):
    """Attempts to find if object attribute might have been misspelled"""
    _ = current_lang.translate

    if obj_type == "builtin_function_or_method":
        obj_name = tb_data.bad_line.replace("." + attribute, "")
        # Confirm we have the right one
        if obj_name in dir(builtins):
            cause = _(
                "`{obj_name}` is a function. Perhaps you meant to write\n"
                "`{obj_name}({attribute})`\n"
            ).format(obj_name=obj_name, attribute=attribute)
            hint = _("Did you mean `{obj_name}({attribute})`?\n").format(
                obj_name=obj_name, attribute=attribute
            )
            return {"cause": cause, "suggest": hint}
        else:
            cause = _(
                "`{obj_name}` is a Python built-in function or method\n"
                "which does not have an attribute named `{attribute}.`\n"
            ).format(obj_name=obj_name, attribute=attribute)
            return {"cause": cause}

    obj = info_variables.get_object_from_name(obj_type, frame)
    if obj is None:
        debug_helper.log("obj is None in attribute_error_in_object.")
        return {"cause": internal_error()}

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)["name, obj"]
    for obj_name, instance in all_objects:
        if isinstance(instance, obj) or instance == obj:
            break
    else:
        debug_helper.log("object is not on bad_line in attribute_error_in_object.")
        return {"cause": internal_error()}

    possible_cause = tuple_by_accident(instance, obj_name, attribute)
    if possible_cause:
        return possible_cause

    known_attributes = dir(instance)

    # Example: this.len -> len(this)
    known_builtin = perhaps_builtin(attribute, known_attributes)
    if known_builtin:
        return use_builtin_function(obj_name, attribute, known_builtin)

    if attribute == "join":
        join = perhaps_join(obj)
        if join:
            return use_str_join(obj_name)

    # Example: both "this" and "that" are known objects
    # this.that -> this, that
    if attribute in frame.f_globals or attribute in frame.f_locals:
        return missing_comma(obj_name, attribute)

    known_synonyms = perhaps_synonym(attribute, known_attributes)
    if known_synonyms:
        return use_synonym(obj_name, attribute, known_synonyms)

    # noqa Example: list.apend -> list.append
    similar = get_similar_words(attribute, known_attributes)
    if similar:
        return handle_attribute_typo(obj_name, attribute, similar)

    # We have not been able to find a useful suggestion
    cause = _("The object `{obj}` has no attribute named `{attr}`.\n").format(
        obj=obj_name, attr=attribute
    )
    if hasattr(obj, "__slots__"):
        cause += _(
            "Note that object `{obj}` uses `__slots__` which prevents\n"
            "the creation of new attributes.\n"
        ).format(obj=obj_name)
    known_attributes = [a for a in known_attributes if "__" not in a]
    if len(known_attributes) > 10:
        known_attributes = known_attributes[:9] + ["..."]
    if known_attributes:
        cause += _(
            "The following are some of its known attributes:\n" "`{names}`."
        ).format(names=", ".join(known_attributes))
    return {"cause": cause}


def handle_attribute_typo(obj_name, attribute, similar):
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
        names = list_to_string(similar)
        hint = _("Did you mean one of the following: `{names}`?\n").format(names=names)
        cause = _(
            "Instead of writing `{obj}.{typo}`, perhaps you meant to write one of \n"
            "the following names which are attributes of object `{obj}`:\n"
            "`{names}`\n"
        ).format(names=names, typo=attribute, obj=obj_name)
    return {"cause": cause, "suggest": hint}


def perhaps_builtin(attribute, known_attributes):
    if attribute in ["min", "max", "sorted", "reversed", "sum"]:
        return attribute
    if (
        attribute in ["len", "length", "lenght"]  # noqa
        and "__len__" in known_attributes
    ):
        return "len"


def tuple_by_accident(obj, obj_name, attribute):
    _ = current_lang.translate
    if not (isinstance(obj, tuple) and len(obj) == 1):
        return {}

    true_obj = obj[0]
    if hasattr(true_obj, attribute):
        hint = _("Did you write a comma by mistake?\n")
        cause = _(
            "`{obj_name}` is a tuple that contains a single item\n"
            "which does have `'{attribute}'` as an attribute.\n"
            "Perhaps you added a trailing comma by mistake at the end of the line\n"
            "where you defined `{obj_name}`.\n"
        ).format(obj_name=obj_name, attribute=attribute)
        return {"cause": cause, "suggest": hint}

    return {}


def use_str_join(obj_name):
    _ = current_lang.translate
    hint = _("Did you mean `'...'.join({obj_name})`?\n").format(obj_name=obj_name)
    cause = _(
        "The object `{obj_name}` has no attribute named `join`.\n"
        "Perhaps you wanted something like `'...'.join({obj_name})`.\n"
    ).format(obj_name=obj_name)
    return {"cause": cause, "suggest": hint}


def use_builtin_function(obj_name, attribute, known_builtin):
    _ = current_lang.translate
    hint = _("Did you mean `{known_builtin}({obj_name})`?\n").format(
        known_builtin=known_builtin, obj_name=obj_name
    )
    cause = _(
        "The object `{obj_name}` has no attribute named `{attribute}`.\n"
        "Perhaps you can use the Python builtin function `{known_builtin}` instead:\n"
        "`{known_builtin}({obj_name})`."
    ).format(known_builtin=known_builtin, obj_name=obj_name, attribute=attribute)
    return {"cause": cause, "suggest": hint}


def perhaps_join(obj):
    if hasattr(obj, "__iter__") or (
        hasattr(obj, "__getitem__") and hasattr(obj, "__len__")
    ):
        return True


def perhaps_synonym(attribute, known_attributes):
    synonyms = [
        ["add", "append", "extend", "insert", "push", "update", "union"],
        ["remove", "discard", "pop"],
    ]
    for syn_list in synonyms:
        if attribute in syn_list:
            result = []
            for attr in syn_list:
                if attr in known_attributes:
                    result.append(attr)
            if result:
                return result


def use_synonym(obj_name, attribute, synonyms):
    _ = current_lang.translate

    hint = _("Did you mean `{attr}`?\n").format(attr=synonyms[0])

    cause = _("The object `{name}` has no attribute named `{attribute}`.\n").format(
        name=obj_name, attribute=attribute
    )

    if len(synonyms) == 1:
        cause += _(
            "However, `{attr}` is an attribute of `{name}` with a similar meaning.\n"
        ).format(name=obj_name, attribute=attribute)
    else:
        cause += _(
            "However, `{name}` has the following attributes with similar meanings:\n"
            "`{attributes}`.\n"
        ).format(name=obj_name, attributes=list_to_string(synonyms))

    return {"cause": cause, "suggest": hint}


def missing_comma(first, second):
    _ = current_lang.translate

    hint = _("Did you mean to separate object names by a comma?\n")

    cause = _(
        "`{second}` is not an attribute of `{first}`.\n"
        "However, both `{first}` and `{second}` are known objects.\n"
        "Perhaps you wrote a period to separate these two objects, \n"
        "instead of using a comma.\n"
    ).format(first=first, second=second)

    return {"cause": cause, "suggest": hint}
