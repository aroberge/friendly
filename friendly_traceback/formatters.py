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


# TODO: support verbosity instead of level


def format_traceback(info, level=1):
    """ Simple text formatter for the traceback."""
    result = choose_formatter[level](info, level=level)
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


def traceback_before_default(info, level=2, **kwargs):
    """Includes the Python traceback before all the information
       processed by Friendly-traceback.
    """
    result = [info["simulated_python_traceback"]]
    result.extend(default(info))
    return result


def traceback_after_default(info, level=3, **kwargs):
    """Includes the Python traceback after all the information
       processed by Friendly-traceback.
    """
    result = default(info)
    result.extend(info["simulated_python_traceback"])
    return result


def no_generic_explanation(info, level=4, **kwargs):
    """Similar to the default option except that it does not display the
       generic information about a given exception.
    """
    items = friendly_items
    spacing = {"indent": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item, formatting in items:
        if item == "generic":
            continue
        if item in info:
            for line in info[item].split("\n"):
                result.append(spacing[formatting] + line)
    return result


def traceback_before_no_generic(info, level=5, **kwargs):
    """Includes the Python traceback before all the information
       processed by Friendly-traceback.
    """
    result = [info["simulated_python_traceback"]]
    result.extend(no_generic_explanation(info))
    return result


def traceback_after_no_generic(info, level=6, **kwargs):
    """Includes the Python traceback after all the information
       processed by Friendly-traceback.
    """
    result = no_generic_explanation(info)
    result.extend(info["simulated_python_traceback"])
    return result


def simple_explain(info, level=7, **kwargs):
    """7: (Subject to change) Python tracebacks followed
               by specific information.
    """
    items = [
        ("simulated_python_traceback", "none")(
            "parsing_error", "indent"
        ),  # only for SyntaxError ...
        ("cause", "double"),
    ]
    spacing = {"indent": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item, formatting in items:
        if item in info:
            for line in info[item].split("\n"):
                result.append(spacing[formatting] + line)
    return result


def minimal_for_console(info, level=8, **kwargs):
    """Minimal traceback, useful for console use by more experienced users.
    """

    only_show = [
        "message",
        "parsing_error_source",
        "cause",
        "last_call_source",
        "last_call_variables",
        "exception_raised_source",
        "exception_raised_variables",
    ]
    spacing = {"indent": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item, formatting in friendly_items:
        if item not in only_show:
            continue
        if item in info:
            for line in info[item].split("\n"):
                result.append(spacing[formatting] + line)
    return result


def only_python_traceback(info, level=9, **kwargs):
    """Shows only the simulated Python traceback
    """
    return info["simulated_python_traceback"]


def markdown(info, level):
    """Traceback formatted with full information but with markdown syntax."""
    result = []
    friendly_items = [
        ("header", "# ", ""),
        ("message", "", ""),
        ("generic", "", ""),
        ("parsing_error", "", ""),
        ("parsing_error_source", "```\n", "```"),
        ("cause_header", "## ", ""),
        ("cause", "", ""),
        ("last_call_header", "## ", ""),
        ("last_call_source", "```\n", "```"),
        ("last_call_variables", "Variables:\n```\n", "```"),
        ("exception_raised_header", "## ", ""),
        ("exception_raised_source", "```\n", "```"),
        ("exception_raised_variables", "Variables:\n```\n", "```"),
    ]

    for item, prefix, suffix in friendly_items:
        if item in info:
            result.append(prefix + info[item] + suffix)
    return "\n\n".join(result)


choose_formatter = {
    1: default,
    2: traceback_before_default,
    3: traceback_after_default,
    4: no_generic_explanation,
    5: traceback_before_no_generic,
    6: traceback_after_no_generic,
    7: simple_explain,
    8: minimal_for_console,
    9: only_python_traceback,
}
