from friendly_traceback.my_gettext import current_lang


def set_cause_indentation_error(value):
    _ = current_lang.translate

    value = str(value)
    if "unexpected indent" in value:
        this_case = _(
            "The line identified above\n"
            "is more indented than expected and \n"
            "does not match the indentation of the previous line.\n"
        )
    elif "expected an indented block" in value:
        this_case = _(
            "The line identified above\n"
            "was expected to begin a new indented block.\n"
        )
    else:
        this_case = _(
            "The line identified above is\n"
            "less indented than the preceding one,\n"
            "and is not aligned vertically with another block of code.\n"
        )
    return this_case
