"""info_variables.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""

import tokenize

from . import utils


def get_var_info(line, frame):
    """Given a line of code and a frame object, it obtains the
       value (repr) of the names found in either the local or global scope.
    """
    tokens = utils.collect_tokens(line)
    loc = frame.f_locals
    glob = frame.f_globals
    names_info = []
    names = []
    for tok in tokens:
        if tok.type == tokenize.NAME:
            name = tok.string
            if name in names:
                continue
            names.append(name)
            result = ""
            if name in loc:
                result = format_var_info(tok, loc)
            elif name in glob:
                result = format_var_info(tok, glob, _global=True)
            if result:
                names_info.append(result)

    if names_info:
        names_info.append("")
    return "\n".join(names_info)


def format_var_info(tok, _dict, _global=""):
    """Formats the variable information so that it fits on a single line
       for each variable.

       The format we want is something like the following:

       [global] name: repr(name)

       However, if repr(name) exceeds a certain value, it is truncated.
       When that is the case, if len(name) is defined, as is the case for
       lists, tuples, dicts, etc., then len(name) is shown on a separate line.
       This can be useful information in case of IndexError and possibly
       others.
    """
    MAX_LENGTH = 50
    length_info = ""
    if _global:
        _global = "global "
    name = tok.string
    obj = _dict[name]
    try:
        value = repr(obj)
    except Exception:
        return ""

    if len(value) > MAX_LENGTH:  # too much text would be shown
        # We reduce the length of the repr, indicate this by ..., but we
        # also keep the last character so that the repr of a list still
        # ends with ], that of a tuple still ends with ), etc.
        value = value[0 : MAX_LENGTH - 5] + "..." + value[-1]
        try:
            length_info = len(obj)
        except TypeError:
            pass

    result = f"    {_global}{name}: {value}"
    if length_info:
        result += f"  | len({name}): {length_info}"
    return result
