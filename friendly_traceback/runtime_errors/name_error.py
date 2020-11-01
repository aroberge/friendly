import re

from ..my_gettext import current_lang
from .. import info_variables


def get_cause(value, info, frame):
    _ = current_lang.translate

    pattern = re.compile(r"name '(.*)' is not defined")
    match = re.search(pattern, str(value))
    if not match:
        return _(
            "No information is known about this exception.\n"
            "Please report this example to\n"
            "https://github.com/aroberge/friendly-traceback/issues\n"
        )

    unknown_name = match.group(1)

    cause = _("In your program, `{var_name}` is an unknown name.\n").format(
        var_name=unknown_name
    )

    hint = info_variables.name_has_type_hint(unknown_name, frame)
    similar = info_variables.get_similar_names(unknown_name, frame)
    if similar["best"] is not None:
        info["suggest"] = _("Did you mean `{name}`?").format(name=similar["best"])

    cause += hint + format_similar_names(unknown_name, similar, hint)
    return cause


def format_similar_names(name, similar, hint):
    """This function formats the names that were found to be similar"""
    _ = current_lang.translate

    nb_similar_names = (
        len(similar["locals"]) + len(similar["globals"]) + len(similar["builtins"])
    )
    if nb_similar_names == 0:
        if hint:
            return ""
        else:
            return _("I have no additional information for you.")

    elif nb_similar_names == 1:
        if similar["locals"]:
            return (
                _("The similar name `{name}` was found in the local scope. ").format(
                    name=str(similar["locals"][0]).replace("'", "")
                )
                + "\n"
            )
        elif similar["globals"]:
            similar_name = similar["globals"][0]
            if name != similar_name:
                return (
                    _(
                        "The similar name `{name}` was found in the global scope. "
                    ).format(name=similar_name.replace("'", ""))
                    + "\n"
                )
            else:
                return (
                    _("The name `{name}` was found in the global scope. ").format(
                        name=name
                    )
                    + "\n"
                )
        else:
            return (
                _("The Python builtin `{name}` has a similar name. ").format(
                    name=str(similar["builtins"][0]).replace("'", "")
                )
                + "\n"
            )

    message = _(
        "Instead of writing `{name}`, perhaps you meant one of the following:\n"
    ).format(name=name)
    if similar["locals"]:
        message += (
            _("*   Local scope: ")
            + str(similar["locals"])[1:-1].replace("'", "`")
            + "\n"
        )
    if similar["globals"]:
        message += (
            _("*   Global scope: ")
            + str(similar["globals"])[1:-1].replace("'", "`")
            + "\n"
        )
    if similar["builtins"]:
        message += (
            _("*   Python builtins: ")
            + str(similar["builtins"])[1:-1].replace("'", "`")
            + "\n"
        )
    return message
