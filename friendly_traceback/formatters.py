"""formatters.py

"""

friendly_items = [
    ("header", "indent"),
    ("generic", "indent"),
    ("location header", "indent"),
    # only for SyntaxError and TabError
    ("location information", "indent"),
    ("cause header", "indent"),
    ("cause", "double indent"),
    ("last_call header", "indent"),
    ("last_call source", "no indent"),
    ("last_call variables", "no indent"),
    ("exception_raised header", "indent"),
    ("exception_raised source", "no indent"),
    ("exception_raised variables", "no indent"),
]


def format_traceback(info, level=1):
    """ Simple text formatter for the traceback."""
    result = choose_formatter[level](info)
    return "\n".join(result)


def default(info):
    """Shows all the information processed by Friendly-traceback with
       formatting suitable for REPL.
    """
    spacing = {"indent": " " * 4, "double indent": " " * 8, "no indent": ""}
    result = [""]
    for item, formatting in friendly_items:
        if item in info:
            for line in info[item].split("\n"):
                result.append(spacing[formatting] + line)
    return result


def python_traceback_before(info):
    """Includes the normal Python traceback before all the information
       processed by Friendly-traceback.
    """
    result = [""]
    result.append(info["python_traceback"])
    result.extend(default(info))
    return result


def python_traceback_after(info):
    """Includes the normal Python traceback after all the information
       processed by Friendly-traceback.
    """
    result = default(info)
    result.append(info["python_traceback"])
    return result


def only_explain(info):
    """Includes the normal Python traceback before adding the generic
       information about a given exception and the likely cause.
    """
    result = [""]
    result.append(info["python_traceback"])
    if "generic" in info:
        result.append("    " + info["generic"])
    if "cause header" in info:
        result.append("    " + info["cause header"])
    if "cause" in info:
        result.append("        " + info["cause"])
    return result


choose_formatter = {
    1: default,
    2: python_traceback_before,
    3: only_explain,
    9: python_traceback_after,
}
