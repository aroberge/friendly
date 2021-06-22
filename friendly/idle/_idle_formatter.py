"""Custom formatter for IDLE.

The logic is quite convoluted, unless one is very familiar with
how the basic formatting is done.

All that matters is that, it is debugged and works appropriately! ;-)
"""
import sys
from friendly.formatters import select_items, no_result, repl_indentation

if sys.version_info >= (3, 9, 5):
    repl_indentation["suggest"] = "single"  # more appropriate value


def format_source(text, keep_caret):
    """Formats the source code shown by where().

    Often, the location of an error is indicated by one or more ^ below
    the line with the error. IDLE uses highlighting with red background the
    normal single character location of an error.
    This function replaces the ^ used to highlight an error by the same
    highlighting scheme used by IDLE.
    """
    lines = text.split("\n")
    while not lines[-1].strip():
        lines.pop()
    caret_set = {"^"}
    error_line = -2
    begin = end = 0
    for index, line in enumerate(lines):
        if set(line.strip()) == caret_set:
            error_line = index
            begin = line.find("^")
            end = begin + len(line.strip())
            break

    new_lines = []
    for index, line in enumerate(lines):
        if index == error_line and not keep_caret:
            continue

        if index == error_line - 1:
            new_lines.append((line[0:begin], "default"))
            new_lines.append((line[begin:end], "ERROR"))
            new_lines.append((line[end:], "default"))
        else:
            new_lines.append((line, "default"))
        new_lines.append(("\n", "default"))
    return new_lines


def format_text(info, item, indentation):
    """Format text with embedded code fragment surrounded by backquote characters."""
    new_lines = []
    text = info[item].rstrip()
    for line in text.split("\n"):
        if "`" in line and line.count("`") % 2 == 0:
            fragments = line.split("`")
            for index, fragment in enumerate(fragments):
                if index == 0:
                    new_lines.append((indentation + fragment, "stdout"))
                elif index % 2:
                    if "Error" in fragment:
                        new_lines.append((fragment, "stderr"))
                    else:
                        new_lines.append((fragment, "default"))
                else:
                    new_lines.append((fragment, "stdout"))
            new_lines.append(("\n", "stdout"))
        else:
            if line.startswith("    "):  # indented code for markdown!
                colour = "default"
            else:
                colour = "stdout"
            new_lines.append((indentation + line + "\n", colour))

    return new_lines


def format_traceback(text):
    """We format tracebacks using the default stderr color (usually red)
    except that lines with code are shown in the default color (usually black).
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("    "):
            new_lines.append((line, "default"))
        elif line:
            new_lines.append((line, "stderr"))
        new_lines.append(("\n", "default"))
    return new_lines


def idle_formatter(info, include="friendly_tb"):
    """Formatter that takes care of color definitions."""
    # The explanation for SyntaxError and subclasses states that the
    # location of the error is indicated by ^
    keep_caret = (
        "SyntaxError" in info["shortened_traceback"]
        or "IndentationError" in info["shortened_traceback"]
        or "TabError" in info["shortened_traceback"]
    )
    items_to_show = select_items(include)
    spacing = {"single": " " * 4, "double": " " * 8, "none": ""}
    result = ["\n"]
    for item in items_to_show:
        if item == "header":
            continue

        if item in info:
            if "traceback" in item:  # no additional indentation
                result.extend(format_traceback(info[item]))
            elif "source" in item:  # no additional indentation
                result.extend(format_source(info[item], keep_caret))
            elif "header" in item:
                indentation = spacing[repl_indentation[item]]
                result.append((indentation + info[item], "stderr"))
            elif item == "message":  # Highlight error name
                parts = info[item].split(":")
                parts[0] = "`" + parts[0] + "`"
                _info = {item: ":".join(parts)}
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(_info, item, indentation))
            else:
                indentation = spacing[repl_indentation[item]]
                result.extend(format_text(info, item, indentation))
            if "traceback" not in item:
                result.extend("\n")

    if result == ["\n"]:
        return no_result(info, include)

    if result[-1] == "\n" and include != "friendly_tb":
        result.pop()

    return result
