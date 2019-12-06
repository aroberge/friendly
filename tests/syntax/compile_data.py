"""Docstring to be written"""

import pprint
import sys
import friendly_traceback
import catch_syntax_error

major = sys.version_info.major
minor = sys.version_info.minor

out_file = f"data_{major}_{minor}.py"

results = {"version": (major, minor)}


def _formatter(info, level=None):
    items = {"cause": None}
    for key in info:
        if key in ("message", "parsing_error_source", "cause"):
            if key in info:
                items[key] = info[key]

    return str(items)  # formatter expect a string


friendly_traceback.set_formatter(formatter=_formatter)

info = {}

for filename in catch_syntax_error.causes:
    try:
        exec("import %s" % filename)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    out = eval(friendly_traceback.get_output())  # convert back to dict.
    info[filename] = out

with open(out_file, "w", encoding="utf8") as f:
    f.write("info = ")
    pprint.pprint(info, stream=f, width=100)
