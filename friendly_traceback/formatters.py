"""formatters.py

"""

friendly_items = [
    "header",
    "generic",
    "cause",
    "last_call header",
    "last_call source",
    "last_call variables",
    "exception_raised header",
    "exception_raised source",
    "exception_raised variables",
]


def format_traceback(info, level=1):
    """ Simple text formatter for the traceback."""
    result = choose_formatter[level](info)
    return "\n".join(result)


def default(info):
    """Shows all the information processed by Friendly-traceback"""
    result = [""]
    for item in friendly_items:
        if item in info:
            result.append(info[item])
    return result


def python_traceback_before(info):
    """Includes the normal Python traceback before all the information
       processed by Friendly-traceback.
    """
    result = [""]
    result.append(info["python_traceback"])
    for item in friendly_items:
        if item in info:
            result.append(info[item])
    return result


def python_traceback_after(info):
    """Includes the normal Python traceback after all the information
       processed by Friendly-traceback.
    """
    result = [""]
    for item in friendly_items:
        if item in info:
            result.append(info[item])
    result.append(info["python_traceback"])
    return result


def only_explain(info):
    """Includes the normal Python traceback before adding the generic
       information about a given exception and the likely cause.
    """
    result = [""]
    result.append(info["python_traceback"])
    for item in ["generic", "cause"]:
        if item in info:
            result.append(info[item])
    return result


choose_formatter = {
    1: default,
    2: python_traceback_before,
    3: only_explain,
    9: python_traceback_after,
}
