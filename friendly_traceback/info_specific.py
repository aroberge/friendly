"""info_specific.py

Attempts to provide some specific information about the likely cause
of a given exception.
"""

import sys

from .my_gettext import current_lang
from . import analyze_syntax
from . import analyze_type_error
from .utils import edit_distance

get_cause = {}


def register(error_name):
    """Decorator used to record as available an explanation for a given exception"""

    def add_exception(function):
        get_cause[error_name] = function

        def wrapper(etype, value):
            return function(etype, value)

        return wrapper

    return add_exception


@register("AttributeError")
def attribute_error(etype, value):
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


@register("FileNotFoundError")
def file_not_found_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # fileNotFoundError: No module named 'does_not_exist'
    #
    # By splitting value using ', we can extract the module name.
    return _(
        "In your program, the name of the\n"
        "file that cannot be found is `{filename}`.\n"
    ).format(filename=str(value).split("'")[1])


@register("ImportError")
def import_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    #  ImportError: cannot import name 'X' from 'Y'  | Python 3.7
    #  ImportError: cannot import name 'X'           | Python 3.6
    #
    #  However, we might also encounter something like
    #  ImportError: No module named X
    #
    # By splitting value using ', we can extract the name and object
    message = str(value)
    if message.startswith("No module named"):
        name = message.split(" ")[-1]
        return _(
            "The name of the module that could not be imported is `{name}`\n"
        ).format(name=name)
    else:
        parts = str(value).split("'")
        name = parts[1]
    if len(parts) > 3:
        module = parts[3]
        return _(
            "The object that could not be imported is `{name}`.\n"
            "The module or package where it was \n"
            "expected to be found is `{module}`.\n"
        ).format(name=name, module=module)
    else:
        return _("The object that could not be imported is `{name}`.\n").format(
            name=name
        )


@register("IndentationError")
def indentation_error(etype, value):
    _ = current_lang.translate

    value = str(value)
    if "unexpected indent" in value:
        this_case = _(
            "In this case, the line identified above\n"
            "is more indented than expected and \n"
            "does not match the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "In this case, the line identified above\n"
            "was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "In this case, the line identified above is\n"
            "less indented than the preceding one,\n"
            "and is not aligned vertically with another block of code.\n"
        )
    return this_case


@register("KeyError")
def key_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # KeyError: 'c'
    #
    # By splitting value using ', we can extract the missing key name.
    return _(
        "In your program, the name of the key\n"
        "that cannot be found is `{key_name}`.\n"
    ).format(key_name=str(value).split("'")[1])


@register("ModuleNotFoundError")
def module_not_found_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # ModuleNotFoundError: No module named 'does_not_exist'
    #
    # By splitting value using ', we can extract the module name.
    return _(
        "In your program, the name of the\n"
        "module that cannot be found is `{mod_name}`.\n"
    ).format(mod_name=str(value).split("'")[1])


@register("NameError")
def name_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # NameError: name 'c' is not defined
    #
    # By splitting value using ', we can extract the variable name.
    #
    # May be overwritten in core.set_call_info()
    return _("In your program, the unknown name is `{var_name}`.\n").format(
        var_name=str(value).split("'")[1]
    )


@register("OverflowError")
def overflow_error(*args):
    return  # No additional information can be provided


@register("SyntaxError")
def syntax_error(etype, value):
    return analyze_syntax.find_likely_cause(value)


@register("TypeError")
def type_error(etype, value):
    return analyze_type_error.convert_message(str(value))


@register("UnboundLocalError")
def unbound_local_error(etype, value):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # UnboundLocalError: local variable 'a' referenced before assignment
    #
    # By splitting value using ', we can extract the variable name.
    return _(
        "The variable that appears to cause the problem is `{var_name}`.\n"
        "Perhaps the statement\n\n"
        "    global {var_name}\n\n"
        "should have been included as the first line inside your function.\n"
    ).format(var_name=str(value).split("'")[1])


@register("ZeroDivisionError")
def zero_division_error(*args):
    return
