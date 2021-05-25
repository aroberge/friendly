"""Common information so that all traceback generating scripts
   create files in the same formatter.

"""
import os
import sys
from contextlib import redirect_stderr

this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, ".."))


import friendly
from syntax_errors_descriptions import descriptions


def write(text):
    sys.stderr.write(text + "\n")

nb = 0

def make_title(text, formatter="pre"):
    global nb
    nb += 1
    if formatter == "pre":
        write("\n" + f"({nb}) " + text)
        write("-" * len(f"({nb}) " + text) + "\n")
        write(".. code-block:: none\n")
    elif formatter == "markdown_docs":
        write("\n---\n")
        write("## " + f"({nb}) " + text)
    else:
        print("Unsupported formatter: ", formatter)
        sys.exit()


cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, "syntax"))


def create_tracebacks(target, intro_text, formatter="pre"):
    with open(target, "w", encoding="utf8") as out, redirect_stderr(out):
        write(intro_text)

        for name in descriptions:
            title = descriptions[name]["title"]
            make_title(title, formatter=formatter)
            try:
                __import__(name)
            except Exception:  # noqa
                friendly.explain_traceback()


print("    Number of cases in trb_syntax_common.py: ", len(descriptions))
