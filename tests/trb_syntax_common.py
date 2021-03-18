"""Common information so that all traceback generating scripts
   create files in the same formatter.

"""
import os
import sys
from contextlib import redirect_stderr
import friendly
from syntax_errors_descriptions import descriptions


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text, formatter="pre"):
    if formatter == "pre":
        write("\n" + text)
        write("-" * len(text) + "\n")
        write(".. code-block:: none\n")
    elif formatter == "markdown_docs":
        write("\n---\n")
        write("## " + text)
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
