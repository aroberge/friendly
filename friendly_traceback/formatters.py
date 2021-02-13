"""
formatters.py
==============

Default formatters showing all or only part of the available information.

A formatter is a function that takes two arguments:

1. a dict (named ``info`` everywhere in friendly-traceback files) containing
   all the information that can be shown to the user, as well as some
   entries that are meant to be used only internally as the full
   friendly-traceback information is obtained.

2. A second argument which is meant to convey what information should be shown.
   This second argument used to be a single integer ("verbosity level").
   It is currently recently being replaced by a single string. However,
   this might change as we experiment with various options prior to
   version 1.0

A formatter returns a single string. By default, this string will be
written to stderr; however this can be changed by the calling program.

This module currently contains 6 formatters:

* ``repl()``: This is used to print the information in a traditional console,
  including that found in IDLE.  The indentation of the traceback itself
  is chosen so as to reproduce that of a normal Python traceback.

* ``pre()``: this produces output with leading spaces so that it can be
  embedded as a code-block in a file (such as .rst). It can also be used
  to print the information in a traditional console, including that
  found in IDLE.

* ``jupyter()``: experimental formatter for Jupyter notebooks

* ``markdown()``: This produces an output formatted with markdown syntax.

* ``markdown_docs()``: This produces an output formatted markdown syntax,
    but where each header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial top headers.

* ``rich_markdown()``: This produces an output formatted with markdown syntax,
    with some modification, with the end result intended to be printed
    in colour in a console using Rich (https://github.com/willmcgugan/rich).
"""
from .my_gettext import current_lang

from .theme import pygments_available

ipython_available = False
if pygments_available:
    try:
        from pygments import highlight  # noqa
        from pygments.lexers import PythonLexer, PythonTracebackLexer  # noqa
        from pygments.formatters import HtmlFormatter  # noqa
        from IPython.display import display, HTML  # noqa

        ipython_available = True
    except ImportError:
        pass

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
    "last_call_variables",
    "exception_raised_header",
    "exception_raised_source",
    "exception_raised_variables",
]


repl_indentation = {
    "header": "single",
    "message": "single",
    "simulated_python_traceback": "none",
    "original_python_traceback": "none",
    "shortened_traceback": "none",
    "suggest": "double",
    "generic": "single",
    "parsing_error": "single",
    "parsing_error_source": "none",
    "cause_header": "single",
    "cause": "single",
    "last_call_header": "single",
    "last_call_source": "none",
    "last_call_variables": "double",
    "exception_raised_header": "single",
    "exception_raised_source": "none",
    "exception_raised_variables": "double",
}


# ===============================
#
#  Next, we have the five formatters.
#
# ===============================


def repl(info, include="friendly_tb"):
    """Default formatter, primarily for console usage.

    The only change made to the content of "info" is
    some added indentation.
    """

    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info:
            indentation = spacing[repl_indentation[item]]
            for line in info[item].split("\n"):
                result.append(indentation + line)

    if result == [""]:
        return no_result(info, include)

    return "\n".join(result)


def html_escape(text):
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n\n", "<br>")
    )
    while "`" in text:
        text = text.replace("`", "<code>", 1)
        text = text.replace("`", "</code>", 1)
    return text


# For some reason, moving this to friendly_traceback.ipython
# and trying to import it from there uninstalls everything: it is as though
# it starts a new iPython subprocess.
def jupyter(info, include="friendly_tb"):
    """Jupyter formatter using pygments and html format."""
    _ = current_lang.translate
    css = HtmlFormatter().get_style_defs(".highlight")
    display(HTML(f"<style>{css}</style>"))
    items_to_show = select_items(include)
    result = False
    for item in items_to_show:
        if item in info:
            result = True
            if "source" in item or "variable" in item:
                text = info[item]
                text = highlight(text, PythonLexer(), HtmlFormatter())
                display(HTML(text))
            elif "traceback" in item:
                text = info[item]
                text = highlight(text, PythonTracebackLexer(), HtmlFormatter())
                display(HTML(text))
            elif item == "message":  # format like last line of traceback
                content = info[item].split(":")
                error_name = content[0]
                if len(content) > 1:
                    message = ":".join(content[1:])
                else:
                    message = ""
                text = "".join(
                    [
                        '<div class="highlight"><pre><span class="gr">',
                        error_name,
                        '</span>: <span class="n">',
                        message,
                        "</span></pre></div>",
                    ]
                )
                display(HTML(text))
            elif item == "suggest":
                text = html_escape(info[item])
                display(HTML(f"<p><i>{text}<i><p>"))
            else:
                text = html_escape(info[item])
                if "header" in item:
                    display(HTML(f"<p><b>{text}</b></p>"))
                else:
                    display(HTML(f'<p style="width: 70ch">{text}</p>'))
    if not result:
        text = ""
        if include == "why":
            text = _("I do not know.")
        elif include == "hint":
            if info["cause"]:
                text = _("I have no suggestion to offer; try `why()`.")
            else:
                text = _("I have no suggestion to offer.")
        if not text:
            return ""
        display(HTML(f'<p style="width: 70ch;">{text}</p>'))

    return ""


if not ipython_available:
    jupyter = repl  # noqa


def pre(info, include="friendly_tb"):
    """Formatter that produces an output that is suitable for
    insertion in a RestructuredText (.rst) code block,
    with pre-formatted indentation.

    The only change made to the content of "info" is
    some added indentation.
    """
    # We first define the indentation to appear before each item
    pre_items = dict(**repl_indentation)

    pre_items.update(
        **{
            "simulated_python_traceback": "single",
            "original_python_traceback": "single",
            "shortened_traceback": "single",
        }
    )

    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = [""]
    for item in items_to_show:
        if item in info and info[item].strip():
            indentation = spacing[pre_items[item]]
            for line in info[item].split("\n"):
                result.append(indentation + line)

    if result == [""]:
        return no_result(info, include)

    return "\n".join(result)


def markdown(info, include="friendly_tb"):
    """Traceback formatted with markdown syntax.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.
    """
    return _markdown(info, include)


def markdown_docs(info, include="explain"):
    """Traceback formatted with markdown syntax, where each
    header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial
    top headers.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    is further processed.
    """
    return _markdown(info, include, docs=True)


def rich_markdown(info, include="friendly_tb"):
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
        "last_call_variables": ("```python\n", "\n```"),
        "exception_raised_header": ("## ", ""),
        "exception_raised_source": ("```python\n", "\n```"),
        "exception_raised_variables": ("```python\n", "\n```"),
        "simulated_python_traceback": ("```pytb\n", "\n```"),
        "original_python_traceback": ("```pytb\n", "\n```"),
        "shortened_traceback": ("```pytb\n", "\n```"),
    }

    items_to_show = select_items(include)  # tb_items_to_show(level=level)
    if rich and include == "explain":
        items_to_show.insert(0, "header")
    result = [""]
    for item in items_to_show:
        if rich and item == "header":  # Skip it here; handled by session.py
            RICH_HEADER = True
            continue
        if item in info and info[item].strip():
            # With normal markdown formatting, it does not make sense to have a
            # header end with a colon.
            # However, we style headers differently with Rich; see
            # Rich theme in file friendly_rich.
            content = info[item]
            if item.endswith("header"):
                if not rich:
                    content = content.rstrip(":")
                else:
                    if item != "cause_header":
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
        return no_result(info, include)
    return "\n\n".join(result)


def no_result(info, include):
    """Should normally only be called if no result is available
    from either hint() or why().
    """
    _ = current_lang.translate
    if include == "why":
        return _("I have no suggestion to offer.")
    elif include == "hint":
        if info["cause"]:
            return _("I have no suggestion to offer; try `why()`.")
        else:
            return _("I have no suggestion to offer.")
    else:
        return f"Internal error: include = {include} in formatters.no_result()"


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
        "last_call_variables",
        "exception_raised_header",
        "exception_raised_source",
        "exception_raised_variables",
    },
    "friendly_tb": {"shortened_traceback", "suggest"},
    "python_tb": {"simulated_python_traceback"},
    "debug_tb": {"original_python_traceback"},
}
items_groups["more"] = items_groups["why"].union(items_groups["where"])
items_groups["explain"] = (
    items_groups["friendly_tb"]
    .union(items_groups["generic"])
    .union(items_groups["more"])
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
