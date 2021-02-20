from .. import debug_helper
from ..my_gettext import current_lang, no_information, internal_error


MESSAGES_PARSERS = []


def add_message_parser(func):
    """A simple decorator that adds a function to parse a specific message
    to the list of known parsers."""
    MESSAGES_PARSERS.append(func)

    def wrapper(*args):
        return func(*args)

    return wrapper


def get_cause(value, frame, tb_data):
    message = str(value)
    try:
        return _get_cause(message, frame, tb_data)
    except Exception:
        debug_helper.log_error()
        return {"cause": internal_error(), "suggest": internal_error()}


def _get_cause(message, frame, tb_data):
    for parser in MESSAGES_PARSERS:
        cause = parser(message, frame, tb_data)
        if cause:
            return cause

    return {"cause": no_information()}


def expression_is_zero(expression, modulo=False):
    """Simpler message when the denominator is a literal 0."""
    _ = current_lang.translate
    try:
        if int(expression) == 0:
            if modulo:
                return _("Using the modulo operator, you are dividing by zero.\n")
            return _("You are dividing by zero.\n")
        else:
            return ""
    except Exception:
        return ""


@add_message_parser
def division_by_zero(message, _frame, tb_data):
    _ = current_lang.translate
    if (
        message != "division by zero"
        and message != "float division by zero"
        and message != "complex division by zero"
    ):
        return {}

    expression = tb_data.bad_line
    if expression.count("/") == 1:
        expression = expression.split("/")[1]
        cause = expression_is_zero(expression)
        if not cause:
            cause = _(
                "You are dividing by the following term\n\n"
                "    {expression}\n\n"
                "which is equal to zero.\n"
            ).format(expression=expression)
    else:
        cause = _(
            "The following mathematical expression includes a division by zero:\n\n"
            "    {expression}\n"
        ).format(expression=expression)
    return {"cause": cause}


@add_message_parser
def integer_or_modulo(message, _frame, tb_data):
    _ = current_lang.translate
    if message != "integer division or modulo by zero":
        return {}
    expression = tb_data.bad_line
    nb_div = expression.count("//")
    nb_mod = expression.count("%")
    nb_divmod = expression.count("divmod")
    if nb_div and not (nb_mod or nb_divmod):
        if nb_div == 1:
            expression = expression.split("//")[1]
            cause = expression_is_zero(expression)
            if not cause:
                cause = _(
                    "You are dividing by the following term\n\n"
                    "    {expression}\n\n"
                    "which is equal to zero.\n"
                ).format(expression=expression)
        else:
            cause = _(
                "The following mathematical expression includes a division by zero:\n\n"
                "    {expression}\n"
            ).format(expression=expression)
    elif nb_mod and not (nb_div or nb_divmod):
        if nb_mod == 1:
            expression = expression.split("%")[1]
            cause = expression_is_zero(expression, modulo=True)
            if not cause:
                cause = _(
                    "Using the modulo operator, you are dividing by the following term\n\n"
                    "    {expression}\n\n"
                    "which is equal to zero.\n"
                ).format(expression=expression)
        else:
            cause = _(
                "The following mathematical expression includes a division by zero:\n\n"
                "    {expression}\n"
            ).format(expression=expression)
    elif nb_divmod and not (nb_div or nb_mod):
        cause = _("The second argument of the `divmod()` function is zero.\n")
    else:
        cause = _(
            "The following mathematical expression includes a division by zero:\n\n"
            "    {expression}\n"
        ).format(expression=expression)

    return {"cause": cause}


@add_message_parser
def zero_negative_power(message, *_ignore):
    _ = current_lang.translate
    if message != "0.0 cannot be raised to a negative power":
        return {}
    cause = _(
        "You are attempting to raise the number 0 to a negative power\n"
        "which is equivalent to dividing by zero.\n"
    )
    return {"cause": cause}


@add_message_parser
def float_modulo(message, _frame, tb_data):
    _ = current_lang.translate
    if message != "float modulo":
        return {}
    expression = tb_data.bad_line
    if expression.count("%") == 1:
        expression = expression.split("%")[1]
        cause = expression_is_zero(expression, modulo=True)
        if not cause:
            cause = _(
                "Using the modulo operator, you are dividing by the following term\n\n"
                "    {expression}\n\n"
                "which is equal to zero.\n"
            ).format(expression=expression)
    else:
        cause = _(
            "The following mathematical expression includes a division by zero\n"
            "done using the modulo operator:\n\n"
            "    {expression}\n"
        ).format(expression=expression)

    return {"cause": cause}


@add_message_parser
def float_divmod(message, *_ignore):
    _ = current_lang.translate
    if message != "float divmod()":
        return {}

    cause = _("The second argument to the `divmod()` function is equal to zero.\n")
    return {"cause": cause}
