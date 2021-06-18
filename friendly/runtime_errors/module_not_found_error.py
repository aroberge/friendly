"""Getting specific information for ModuleNotFoundError"""

import re
import sys

from . import stdlib_modules
from .. import debug_helper
from ..my_gettext import current_lang
from ..utils import get_similar_words, list_to_string, RuntimeMessageParser

parser = RuntimeMessageParser()


@parser.add
def is_not_a_package(value, _frame, _tb_data):
    _ = current_lang.translate
    message = str(value)
    pattern = re.compile(r"No module named '(.*)'; '(.*)' is not a package")
    match = re.search(pattern, message)
    if not match:
        return {}

    dotted_path = match.group(1)
    name = match.group(2)
    rest = dotted_path.replace(name + ".", "")

    # This specific exception should not have been raised if name was not a module.
    # Still, when dealing with imports, better safe than sorry.
    try:
        module = __import__(name)
    except ImportError as e:  # pragma: no cover
        cause = _(
            "No additional information available since `{name}` cannot be imported.\n"
        ).format(name=name)
        debug_helper.log("Problem in is_not_a_package()")
        debug_helper.log(str(e))
        debug_helper.log(cause)
        return {"cause": cause}

    attributes = dir(module)

    if rest in attributes:
        hint = _("Did you mean `from {name} import {rest}`?\n").format(
            name=name, rest=rest
        )
        cause = _(
            "`{rest}` is not a separate module but an object that is part of `{name}`.\n"
        ).format(name=name, rest=rest)
        return {"cause": cause, "suggest": hint}

    similar = get_similar_words(rest, attributes)
    if similar:
        for attr in similar:
            obj = getattr(module, attr)
            if isinstance(obj, type(module)):
                hint = _("Did you mean `import {name}.{attr}`?\n").format(
                    name=name, attr=attr
                )
                cause = _(
                    "Perhaps you meant `import {name}.{attr}`.\n"
                    "`{attr}` is a name similar to `{rest}` and is a module that\n"
                    "can be imported from `{name}`.\n"
                ).format(name=name, attr=attr, rest=rest)
                break
        else:
            attr = similar[0]
            hint = _("Did you mean `from {name} import {attr}`?\n").format(
                name=name, attr=attr
            )
            cause = _(
                "Perhaps you meant `from {name} import {attr}`.\n"
                "`{attr}` is a name similar to `{rest}` and is an object that\n"
                "can be imported from `{name}`.\n"
            ).format(name=name, attr=attr, rest=rest)

        if len(similar) > 1:
            cause += _(
                "Other objects with similar names that are part of\n"
                " `{name}` include `{others}`.\n"
            ).format(name=name, others=list_to_string(similar[1:]))
            return {"cause": cause, "suggest": hint}
    else:
        cause = _("`{rest}` cannot be imported from `{name}`.\n").format(
            rest=rest, name=name
        )

    return {"cause": cause}


def curses_no_found():
    _ = current_lang.translate
    if sys.platform.startswith("win"):
        hint = _("The curses module is rarely installed with Python on Windows.\n")
    else:  # pragma: no cover
        hint = _("The curses module is often not installed with Python.\n")
    cause = _("You have tried to import the curses module.\n")
    return {"cause": cause + hint, "suggest": hint}


@parser.add
def no_module_named(value, _frame, _tb_data):
    _ = current_lang.translate

    message = str(value)
    pattern = re.compile(r"No module named '(.*)'$")
    match = re.search(pattern, message)
    if not match:  # pragma: no cover
        return {}

    name = match.group(1)
    if name == "_curses":
        return curses_no_found()

    similar = get_similar_words(name, stdlib_modules.names)
    cause = _(
        "No module named `{name}` can be imported.\n"
        "Perhaps you need to install it.\n"
    ).format(name=name)
    if not similar:
        return {"cause": cause}

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
    return {"cause": cause, "suggest": hint}
