"""Getting specific information for ImportError"""

from ..my_gettext import current_lang


def get_cause(value, info, frame):
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
