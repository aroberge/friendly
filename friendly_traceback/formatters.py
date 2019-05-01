"""formatters.py

"""

# Currently, we have a single, very basic formatter which simply
# outputs the information gathered "as is".


def format_traceback(info):
    """ Simple text formatter for the traceback."""
    result = [""]
    for item in [
        "header",
        "generic",
        "cause",
        "last_call header",
        "last_call source",
        "last_call variables",
        "exception_raised header",
        "exception_raised source",
        "exception_raised variables",
    ]:
        if item in info:
            result.append(info[item])

    return "\n".join(result)
