"""formatters.py

Default formatters showing all or only part of the available information.
"""

# friendly_items includes all possible keys for info
# except for "python_traceback" and "simulated_python_traceback"
friendly_items = [
    # (key, custom_indentation_code)
    ("header", "indent"),
    ("message", "double"),
    ("generic", "indent"),
    ("parsing_error", "indent"),  # only for SyntaxError ...
    ("parsing_error_source", "none"),  # and subclasses
    ("cause_header", "indent"),
    ("cause", "double"),
    ("last_call_header", "indent"),
    ("last_call_source", "none"),
    ("last_call_variables", "none"),
    ("exception_raised_header", "indent"),
    ("exception_raised_source", "none"),
    ("exception_raised_variables", "none"),
]

explain_items = [
    ("header", "indent"),
    ("message", "double"),
    ("generic", "indent"),
    ("parsing_error", "indent"),  # only for SyntaxError ...
    ("parsing_error_source", "none"),  # and subclasses
    ("cause_header", "indent"),
    ("cause", "double"),
]


def format_traceback(info, level=1):
    """ Simple text formatter for the traceback."""
    result = choose_formatter[abs(level)](info, level=level)
    return "\n".join(result)


def default(info, items=None, **kwargs):
    """Shows all the information processed by Friendly-traceback with
       formatting suitable for REPL.
    """
    if items is None:
        items = friendly_items
    spacing = {"indent": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item, formatting in items:
        if item in info:
            for line in info[item].split("\n"):
                result.append(spacing[formatting] + line)
    return result


def python_traceback_before(info, level=2, **kwargs):
    """Includes the Python traceback before all the information
       processed by Friendly-traceback.
    """
    result = []
    if level > 0:
        result.extend(info["simulated_python_traceback"])
    else:
        result.extend(info["python_traceback"])
    result.extend(default(info))
    return result


def python_traceback_after(info, level=3, **kwargs):
    """Includes the Python traceback after all the information
       processed by Friendly-traceback.
    """
    result = default(info)
    if level > 0:
        result.extend(info["simulated_python_traceback"])
    else:
        result.extend(info["python_traceback"])
    return result


def only_add_explain(info, level=4, **kwargs):
    """Includes the Python traceback before adding the generic
       information about a given exception and the likely cause.
    """
    result = [""]
    if level > 0:
        result.extend(info["simulated_python_traceback"])
    else:
        result.extend(info["python_traceback"])
    result.append("")

    if "generic" in info:
        for line in info["generic"].split("\n"):
            result.append("    " + line)
    if "cause_header" in info:
        for line in info["cause_header"].split("\n"):
            result.append("    " + line)
    if "cause" in info:
        for line in info["cause"].split("\n"):
            result.append("        " + line)
    return result


def only_explain(info, level=5, **kwargs):
    """Only shows the explanation, not where the program stopped
       or the exception was raised.
    """
    result = default(info, items=explain_items)
    return result


def only_python_traceback(info, level=9, **kwargs):
    """Shows only the Python traceback
    """
    if level > 0:
        return info["simulated_python_traceback"]
    else:
        return info["python_traceback"]


choose_formatter = {
    1: default,
    2: python_traceback_before,
    3: python_traceback_after,
    4: only_add_explain,
    5: only_explain,
    9: only_python_traceback,
}
