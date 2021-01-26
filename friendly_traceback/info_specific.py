"""info_specific.py

Attempts to provide some specific information about the likely cause
of a given exception.
"""

from . import debug_helper
from .my_gettext import current_lang


get_cause = {}


def get_likely_cause(etype, value, frame, tb_data):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    cause = hint = None
    try:
        if etype.__name__ in get_cause:
            cause, hint = get_cause[etype.__name__](value, frame, tb_data)
    except Exception as e:
        debug_helper.log("Exception caught in get_likely_cause().")
        debug_helper.log_error(e)
        cause = _(
            "Exception raised by Friendly-traceback itself.\n"
            "Please report this example to\n"
            "https://github.com/aroberge/friendly-traceback/issues\n"
        )
    return cause, hint


def register(error_name):
    """Decorator used to record as available an explanation for a given exception"""

    def add_exception(function):
        get_cause[error_name] = function

        def wrapper(value, frame, tb_data):
            return function(value, frame, tb_data)

        return wrapper

    return add_exception


@register("AttributeError")
def _attribute_error(value, frame, tb_data):
    from .runtime_errors import attribute_error

    return attribute_error.get_cause(value, frame, tb_data)


@register("FileNotFoundError")
def file_not_found_error(value, *_args):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # fileNotFoundError: No module named 'does_not_exist'
    #
    # By splitting value using ', we can extract the module name.
    # TODO: use re instead for added robustness
    return (
        _(
            "In your program, the name of the\n"
            "file that cannot be found is `{filename}`.\n"
        ).format(filename=str(value).split("'")[1]),
        None,
    )


@register("ImportError")
def _import_error(value, frame, tb_data):
    from .runtime_errors import import_error

    return import_error.get_cause(value, frame, tb_data)


@register("IndexError")
def _index_error(value, frame, tb_data):
    from .runtime_errors import index_error

    return index_error.get_cause(value, frame, tb_data)


@register("KeyError")
def key_error(value, *_args):
    _ = current_lang.translate
    # str(value) is expected to be something like
    #
    # KeyError: 'c'
    # TODO: extract to separate file and see if similar keys can be found.
    return (
        _("In your program, the key that cannot be found is `{key_name!r}`.\n").format(
            key_name=value.args[0]
        ),
        None,
    )


@register("ModuleNotFoundError")
def _module_not_found_error(value, frame, tb_data):

    from .runtime_errors import module_not_found_error

    return module_not_found_error.get_cause(value, frame, tb_data)


@register("NameError")
def name_error(value, frame, tb_data):

    from .runtime_errors import name_error

    return name_error.get_cause(value, frame, tb_data)


@register("OverflowError")
def overflow_error(*_args):
    return None, None  # TODO: check to see if additional information
    # can be provided for real test cases


@register("TypeError")
def _type_error(value, frame, tb_data):
    from .runtime_errors import type_error

    return type_error.get_cause(value, frame, tb_data)


@register("ValueError")
def _value_error(value, frame, tb_data):
    from .runtime_errors import value_error

    return value_error.get_cause(value, frame, tb_data)


@register("UnboundLocalError")
def _unbound_local_error(value, frame, tb_data):
    from .runtime_errors import unbound_local_error

    return unbound_local_error.get_cause(value, frame, tb_data)


@register("ZeroDivisionError")
def zero_division_error(*_args):
    # TODO: add explanation for three different cases.
    return None, None  # No additional information can be provided
