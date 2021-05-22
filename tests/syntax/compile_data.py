"""Docstring to be written"""

import pprint
import sys
import os

cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, ".."))
sys.path.append(os.path.join(cur_dir, "..", ".."))
import friendly

import catch_syntax_error

major = sys.version_info.major
minor = sys.version_info.minor

out_file = f"data_{major}_{minor}.py"

results = {"version": (major, minor)}


def _formatter(info, include=None):
    items = {"cause": None}
    for key in info:
        if key in ("message", "parsing_error_source", "cause"):
            if key in info:
                items[key] = info[key]

    return str(items)  # formatter expect a string


friendly.set_formatter(formatter=_formatter)

info = {}

for filename in catch_syntax_error.descriptions:
    try:
        exec("import %s" % filename)
    except Exception:
        friendly.explain_traceback(redirect="capture")
    out = eval(friendly.get_output())  # convert back to dict.
    info[filename] = out

with open(out_file, "w", encoding="utf8") as f:
    f.write("info = ")
    pprint.pprint(info, stream=f, width=100)
