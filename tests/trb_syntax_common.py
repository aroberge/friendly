"""Common information so that all traceback generating scripts
   create files in the same format.

"""
import os
import sys
from contextlib import redirect_stderr
import friendly_traceback
from syntax_errors_descriptions import descriptions


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text, format="pre"):
    if format == "pre":
        write("\n" + text)
        write("-" * len(text) + "\n")
        write(".. code-block:: none\n")
    elif format == "markdown_docs":
        write("\n---\n")
        write("## " + text)
    else:
        print("Unsupported format: ", format)
        sys.exit()


cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, "syntax"))

def create_tracebacks(target, intro_text, format="pre"):
    with open(target, "w", encoding="utf8") as out:
        with redirect_stderr(out):
            write(intro_text)

            for name in descriptions:
                function = None
                title = descriptions[name]["title"]
                make_title(title, format=format)
                try:
                    mod = __import__(name)
                except Exception:
                    friendly_traceback.explain_traceback()


print("    Number of cases in trb_syntax_common.py: ", len(descriptions))
