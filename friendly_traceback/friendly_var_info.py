"""friendly_var_info.py

Used to provide basic variable information in a way that
can be useful for beginners without overwhelming them.
"""

import tokenize

from . import utils


MAX_LENGTH = 50
Unknown = object()


def get_var_info(line, frame):
    tokens = utils.collect_tokens(line)
    loc = frame.f_locals
    glob = frame.f_globals
    results = []
    for tok in tokens:
        result = ""
        if tok.type == tokenize.NAME:
            if tok.string in loc:
                result = format_var_info(tok, loc)
            elif tok.string in glob:
                result = format_var_info(tok, glob, _global=True)
            if result:
                results.append(result)

    if results:
        results.append("")
    return results


def format_var_info(tok, _dict, _global=""):

    length_info = ""
    if _global:
        _global = "global "
    name = tok.string
    obj = _dict[name]
    value = Unknown
    try:
        value = repr(obj)
    except Exception:
        pass
    if value is not Unknown:
        if len(value) > MAX_LENGTH:
            value = value[0 : MAX_LENGTH - 10] + "... " + value[-1]  # noqa
            try:
                length_info = len(obj)
            except TypeError:
                pass

    result = "    {_global}{name}: {value}".format(
        _global=_global, name=name, value=value
    )
    if length_info:
        result += "  | len({name}): {length}".format(name=name, length=length_info)
    return result
