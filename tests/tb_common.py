"""Common information so that all traceback generating scripts
   create files in the same format.

   IMPORTANT: this assumes that all tests files with names of the form

       raise_something.py

"""
import sys
from contextlib import redirect_stderr

import friendly_traceback


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text):
    write("\n" + text)
    write("-" * len(text) + "\n")
    write("Example::\n")


all_imports = {
    "IndentationError - 1: expected an indented block": "raise_indentation_error1",
    "IndentationError - 2: unexpected indent": "raise_indentation_error2",
    "IndentationError - 3: no match ...": "raise_indentation_error3",
    "NameError": ("raise_name_error", "test"),
}


def create_tracebacks(target, intro_text):
    with open(target, "w", encoding="utf8") as out:
        with redirect_stderr(out):
            write(intro_text)

            for title in all_imports:
                function = None
                if isinstance(all_imports[title], tuple):
                    name, function = all_imports[title]
                else:
                    name = all_imports[title]
                make_title(title)
                try:
                    mod = __import__(name)
                    if function is not None:
                        getattr(mod, function)()
                except Exception:
                    friendly_traceback.explain(*sys.exc_info())
