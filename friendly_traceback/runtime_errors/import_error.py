"""Getting specific information for ImportError"""

import re

from ..my_gettext import current_lang


def get_cause(value, info, frame):
    _ = current_lang.translate

    message = str(value)

    pattern = re.compile(r"No module named '(.*)'")
    match = re.search(pattern, message)
    if match:
        return no_module_named(match.group(1), info, frame)

    # Python 3.7+
    pattern2 = re.compile(r"cannot import name '(.*)' from '(.*)'")
    match = re.search(pattern2, message)
    if match:
        return cannot_import_name_from(match.group(1), match.group(2))

    # Python 3.6
    pattern3 = re.compile(r"cannot import name '(.*)'")
    match = re.search(pattern3, message)
    if match:
        return cannot_import_name(match.group(1))

    return _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )


def no_module_named(name, info, frame):
    _ = current_lang.translate
    return _("The name of the module that could not be imported is `{name}`\n").format(
        name=name
    )


def cannot_import_name_from(name, module):
    _ = current_lang.translate
    return _(
        "The object that could not be imported is `{name}`.\n"
        "The module or package where it was \n"
        "expected to be found is `{module}`.\n"
    ).format(name=name, module=module)


def cannot_import_name(name):
    # Python 3.6 does not give us the name of the module
    _ = current_lang.translate
    return _("The object that could not be imported is `{name}`.\n").format(name=name)
