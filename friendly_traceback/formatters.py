"""formatters.py

Default formatters showing all or only part of the available information.
"""

default_items_in_order = [  # This list excludes two full traceback items
    "header",
    "message",
    "generic",
    "parsing_error",
    "parsing_error_source",
    "cause_header",
    "cause",
    "last_call_header",
    "last_call_source",
    "last_call_variables_header",
    "last_call_variables",
    "exception_raised_header",
    "exception_raised_source",
    "exception_raised_variables_header",
    "exception_raised_variables",
]


def tb_items_to_show(level=1):
    """Given a verbosity level, returns a list of traceback items to show."""
    selector = {
        1: _default,
        2: _traceback_before_default,
        3: _traceback_after_default,
        4: _no_generic_explanation,
        5: _traceback_before_no_generic,
        6: _traceback_after_no_generic,
        7: _minimal_for_console,
        8: _simple_explain,
        9: _simulated_python_traceback,
        0: _original_python_traceback,
    }
    return selector[level]()


def format_traceback(info, level=1):
    """Default formatter. Produces an output that is suitable for
       insertion in a RestructuredText (.rst) code block,
       with pre-formatted indentation.

       It is also the default used in the friendly-console.
    """

    pre_items = {
        "header": "single",
        "message": "double",
        "generic": "single",
        "parsing_error": "single",
        "parsing_error_source": "none",
        "cause_header": "single",
        "cause": "double",
        "last_call_header": "single",
        "last_call_source": "none",
        "last_call_variables_header": "double",
        "last_call_variables": "double",
        "exception_raised_header": "single",
        "exception_raised_source": "none",
        "exception_raised_variables_header": "double",
        "exception_raised_variables": "double",
        "simulated_python_traceback": "none",
        "original_python_traceback": "none",
    }

    items_to_show = tb_items_to_show(level=level)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info:
            indentation = spacing[pre_items[item]]
            for line in info[item].split("\n"):
                result.append(indentation + line)
    return "\n".join(result)


def markdown(info, level):
    """Traceback formatted with with markdown syntax.
    """
    result = _markdown(info, level)
    return "\n\n".join(result)


def rich_markdown(info, level):
    """Traceback formatted with with markdown syntax with small tweaks
       using with Rich.
    """
    result = _markdown(info, level, rich=True)
    return "\n\n".join(result)


def _markdown(info, level, rich=False):
    """Traceback formatted with with markdown syntax.
    """
    result = []

    markdown_items = {
        "header": ("# ", ""),
        "message": ("## ", ""),
        "generic": ("", ""),
        "parsing_error": ("", ""),
        "parsing_error_source": ("```python\n", "\n```"),
        "cause_header": ("### ", ""),
        "cause": ("", ""),
        "last_call_header": ("## ", ""),
        "last_call_source": ("```python\n", "\n```"),
        "last_call_variables_header": ("### ", ""),
        "last_call_variables": ("```python\n", "\n```"),
        "exception_raised_header": ("## ", ""),
        "exception_raised_source": ("```python\n", "\n```"),
        "exception_raised_variables_header": ("### ", ""),
        "exception_raised_variables": ("", ""),
        "simulated_python_traceback": ("```python\n", "\n```"),
        "original_python_traceback": ("```python\n", "\n```"),
    }

    items_to_show = tb_items_to_show(level=level)
    result = [""]
    for item in items_to_show:
        if item in info:
            # With normal markdown formatting, it does not make sense to have a
            # header end with a colon.
            # However, we style headers differently with Rich; see
            # Rich theme in file friendly_rich.
            content = info[item]
            if item.endswith("header"):
                if not rich:
                    content = content.rstrip(":")
                else:
                    if item not in [
                        "cause_header",
                        "last_call_variables_header",
                        "exception_raised_variables_header",
                    ]:
                        content = content.rstrip(":")
            if item == "message":
                # replacing something like
                #   the variable 'x' is ...
                # by
                #   the variable '`x`' is ...
                # so that it is highlighted as code.
                content = (
                    content.replace(" '", " '`")
                    .replace("' ", "`' ")
                    .replace("'\n", "`'\n")
                    .replace("'.", "`'.")
                )

            if item.endswith("variables"):
                parts = content.split(":")
                if len(parts) > 1:
                    if parts[1].strip().startswith("<"):
                        content = content.replace("<", '"<').replace(">", '>"')

            prefix, suffix = markdown_items[item]
            result.append(prefix + content + suffix)
    return result


def _default():
    """Includes all the information processed by Friendly-traceback
       which does not include a traditional Python traceback
    """
    return default_items_in_order[:]


def _traceback_before_default():
    """Includes the simulated Python traceback before all the information
       processed by Friendly-traceback.
    """
    items = ["simulated_python_traceback"]
    items.extend(_default())
    return items


def _traceback_after_default():
    """Includes the simulated Python traceback after all the information
       processed by Friendly-traceback.
    """
    items = _default()
    items.append("simulated_python_traceback")
    return items


def _no_generic_explanation():
    """Similar to the default option except that it does not display the
       generic information about a given exception.
    """
    items = []
    for item in default_items_in_order:
        if item == "generic":
            continue
        items.append(item)
    return items


def _traceback_before_no_generic():
    """Includes the simulated Python traceback before all the information
       processed by Friendly-traceback.
    """
    items = ["simulated_python_traceback"]
    items.extend(_no_generic_explanation())
    return items


def _traceback_after_no_generic():
    """Includes the simulated Python traceback after all the information
       processed by Friendly-traceback.
    """
    items = _no_generic_explanation()
    items.append("simulated_python_traceback")
    return items


def _minimal_for_console():
    """Minimal traceback, useful for console use by more experienced users.
    """
    return [
        "message",
        "parsing_error_source",
        "cause",
        "last_call_source",
        "last_call_variables",
        "exception_raised_source",
        "exception_raised_variables",
    ]


def _simple_explain():  # Not (yet) included by Thonny
    """(Subject to change) Simulated Python tracebacks followed
               by specific information.
    """
    return ["simulated_python_traceback", "parsing_error", "cause"]


def _simulated_python_traceback():
    """Shows only the simulated Python traceback
    """
    return ["simulated_python_traceback"]


def _original_python_traceback():
    """Shows only the original Python traceback, which includes calls
       to friendly-traceback itself. It should only be used for diagnostic.
    """
    return ["original_python_traceback"]
