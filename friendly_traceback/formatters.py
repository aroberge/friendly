"""formatters.py

Default formatters showing all or only part of the available information.

A formatter is a function that takes two arguments::

1. a dict (named ``info`` everywhere in friendly-traceback files) containing
   all the information that can be shown to the user, as well as some
   entries that are meant to be used only internally as the full
   friendly-traceback information is obtained.

2. A second argument which is meant to convey what information should be shown.
   This second argument used to be a single integer ("verbosity level").
   It is currently recently being replaced by a string. However,
   this might change as we experiment with various options prior to
   version 1.0

A formatter returns a single string. By default, this string will be
written to stderr; however this can be changed by the calling program.

This module currently contains 4 formatters:

* ``pre()``: this produces output with leading spaces so that it can be
  embedded as a code-block in a file (such as .rst). It can also be used
  to print the information in a traditional console, including that
  found in IDLE.

* ``markdown()``: This produces an output formatted with markdown syntax.

* ``markdown_docs()``: This produces an output formatted markdown syntax,
    but where each header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial top headers.

* ``rich_markdown()``: This produces an output formatted with markdown syntax,
    with some modification, with the end result intended to be printed
    in colour in a console using Rich (https://github.com/willmcgugan/rich).
"""
from .my_gettext import current_lang

RICH_HEADER = False

# The following is the order in which the various items, if they exist
# and have been selected to be printed, would be printed.
# If you are writing a custom formatter, this should be taken as the
# authoritative list of items to consider.

items_in_order = [
    "header",
    "message",  # The last line of a Python traceback
    "original_python_traceback",
    "simulated_python_traceback",
    "shortened_traceback",
    "suggest",
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


# ===============================
#
#  Next, we have the four formatters.
#
# ===============================


def pre(info, include="minimal"):
    """Default formatter, primarily for console usage.

    It also  produces an output that is suitable for
    insertion in a RestructuredText (.rst) code block,
    with pre-formatted indentation.

    The only change made to the content of "info" is
    some added indentation.
    """
    # We first define the indentation to appear before each item
    pre_items = {
        "header": "single",
        "message": "double",
        "suggest": "double",
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
        "simulated_python_traceback": "single",
        "original_python_traceback": "single",
        "shortened_traceback": "single",
    }

    # items_to_show = tb_items_to_show(level=level)
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info:
            indentation = spacing[pre_items[item]]
            for line in info[item].split("\n"):
                result.append(indentation + line)

    if result == [""]:
        return _no_result(info, include)

    return "\n".join(result)


def markdown(info, include="minimal"):
    """Traceback formatted with markdown syntax.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.
    """
    return _markdown(info, include)


def markdown_docs(info, include="minimal"):
    """Traceback formatted with markdown syntax, where each
    header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial
    top headers.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    is further processed.
    """
    return _markdown(info, include, docs=True)


def rich_markdown(info, include="minimal"):
    """Traceback formatted with with markdown syntax suitable for
    printing in color in the console using Rich.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.

    Some additional processing is done just prior to doing the
    final output, by ``session._write_err()``.
    """
    return _markdown(info, include, rich=True)


def _markdown(info, include, rich=False, docs=False):
    """Traceback formatted with with markdown syntax."""
    global RICH_HEADER
    RICH_HEADER = False
    result = []

    markdown_items = {
        "header": ("# ", ""),
        "message": ("", ""),
        "suggest": ("", "\n"),
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
        "exception_raised_variables": ("```python\n", "\n```"),
        "simulated_python_traceback": ("```pytb\n", "\n```"),
        "original_python_traceback": ("```pytb\n", "\n```"),
        "shortened_traceback": ("```pytb\n", "\n```"),
    }

    items_to_show = select_items(include)  # tb_items_to_show(level=level)
    result = [""]
    for item in items_to_show:
        if rich and item == "header":  # Skip it here; handled by session.py
            RICH_HEADER = True
            continue
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
            if item == "message" and rich:
                # Ensure that the exception name is highlighted.
                content = content.split(":")
                content[0] = "`" + content[0] + "`"
                content = ":".join(content)

            prefix, suffix = markdown_items[item]
            if docs:
                if prefix.startswith("#"):
                    prefix = "##" + prefix
            result.append(prefix + content + suffix)

    if result == [""]:
        return _no_result(info, include)
    return "\n\n".join(result)


def _no_result(info, include):
    """Should normally only be called if no result is available
    from either hint() or why().
    """
    _ = current_lang.translate
    if include == "why":
        return _("I do not know.")
    elif include == "hint":
        if info["cause"]:
            return _("I have no suggestion to offer; try `why()`.")
        else:
            return _("I have no suggestion to offer.")
    else:
        return f"Internal error: include = {include} in formatters._no_result()"


items_groups = {
    "header": {"header"},
    "message": {"message"},  # Also included as last line of traceback
    "hint": {"suggest"},
    "generic": {"generic"},
    "what": {"message", "generic"},  # Only include "message" here.
    "why": {"cause"},
    "where": {
        "parsing_error",
        "parsing_error_source",
        "last_call_header",
        "last_call_source",
        "last_call_variables_header",
        "last_call_variables",
        "exception_raised_header",
        "exception_raised_source",
        "exception_raised_variables_header",
        "exception_raised_variables",
    },
    "friendly_tb": {"shortened_traceback"},
    "python_tb": {"simulated_python_traceback"},
    "debug_tb": {"original_python_traceback"},
}
items_groups["minimal"] = (
    items_groups["header"]
    .union(items_groups["friendly_tb"])
    .union(items_groups["hint"])
)
items_groups["more"] = (
    items_groups["header"].union(items_groups["why"]).union(items_groups["where"])
)
items_groups["explain"] = (
    items_groups["minimal"].union(items_groups["generic"]).union(items_groups["more"])
)
items_groups["no_tb"] = items_groups["explain"]
items_groups["no_tb"].discard(items_groups["friendly_tb"])


def select_items(group_name):
    items = items_groups[group_name]
    ordered_items = []
    for item in items_in_order:
        if item in items:
            ordered_items.append(item)
    return ordered_items


# def make_item_selector(items):
#     def selector():
#         return select_items(items)

#     return selector()


# def tb_items_to_show(level=1):
#     """Given a verbosity level, returns a list of traceback items to show."""
#     if level == 1:
#         return make_item_selector("explain")
#     elif level == 2:
#         return make_item_selector("no_tb")
#     selector = {
#         1: _traceback_before_default,  # for running script in non-interactive mode
#         2: _default,  # used to be level 1
#         3: _traceback_before_default,  # same as 1
#         4: _traceback_before_no_generic,
#         5: _no_generic_explanation,  # define as more
#         6: _traceback_after_no_generic,
#         7: _tb_plus_suggest,  # shortened traceback, default for console
#         8: _advanced_user,
#         9: _shortened_python_traceback,
#         0: _simulated_python_traceback,
#         -1: _original_python_traceback,
#         11: _what,
#         12: _where,
#         13: _why,
#         14: _suggest,
#     }
#     return selector[level]()


# def _default():
#     """Includes all the information processed by Friendly-traceback
#     which does not include a traditional Python traceback
#     """
#     return select_items("no_tb")


# def _traceback_before_default():
#     """Includes the simulated Python traceback before all the information
#     processed by Friendly-traceback.
#     """
#     return select_items("explain")


# def _traceback_after_default():
#     """Includes the simulated Python traceback after all the information
#     processed by Friendly-traceback.
#     """
#     items = _default()
#     items.append("shortened_traceback")
#     return items


# def _no_generic_explanation():
#     """Similar to the default option except that it does not display the
#     generic information about a given exception.
#     """
#     items = []
#     for item in items_in_order:
#         if item == "generic":
#             continue
#         items.append(item)
#     return items


# def _traceback_before_no_generic():
#     """Includes the simulated Python traceback before all the information
#     processed by Friendly-traceback.
#     """
#     items = ["shortened_traceback"]
#     items.extend(_no_generic_explanation())
#     return items


# def _traceback_after_no_generic():
#     """Includes the simulated Python traceback after all the information
#     processed by Friendly-traceback.
#     """
#     items = _no_generic_explanation()
#     items.append("shortened_traceback")
#     return items


# def _advanced_user():  # Not (yet) included by Thonny
#     """Useful information for advanced users."""
#     return [
#         "header",
#         "simulated_python_traceback",
#         "suggest",
#         "parsing_error_source",
#         "cause",
#         "last_call_header",
#         "last_call_source",
#         "last_call_variables",
#         "exception_raised_header",
#         "exception_raised_source",
#         "exception_raised_variables",
#     ]


# def _tb_plus_suggest():
#     """Shortened Python tracebacks followed by specific information."""
#     return select_items("explain")


# def _simulated_python_traceback():
#     """Shows only the simulated Python traceback"""
#     return ["simulated_python_traceback"]


# def _shortened_python_traceback():
#     """Shows only the simulated Python traceback"""
#     return ["shortened_traceback"]


# def _original_python_traceback():
#     """Shows only the original Python traceback, which includes calls
#     to friendly-traceback itself. It should only be used for diagnostic.
#     """
#     return ["original_python_traceback"]


# def _what():
#     """Shows the message and and the generic meaning.

#     For example: A NameError means ...
#     """
#     return ["message", "generic"]


# def _why():
#     """Show only the likely cause"""
#     return ["cause"]


# def _suggest():
#     """Show only the hint/suggestion if available"""
#     return ["suggest"]


# def _where():
#     """Shows the locations where the program stopped and where the
#     exception was raised, together with variable information
#     at these locations.
#     """
#     return [
#         "parsing_error",
#         "parsing_error_source",
#         "last_call_header",
#         "last_call_source",
#         "last_call_variables",
#         "exception_raised_header",
#         "exception_raised_source",
#         "exception_raised_variables",
#     ]
