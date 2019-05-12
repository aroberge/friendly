"""Common information so that all traceback generating scripts
   create files in the same format.

Only includes cases for which the information given by Python 3.6
differs from that given by Python 3.7.

"""
import sys
from contextlib import redirect_stderr

import friendly_traceback


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text):
    write("\n" + text)
    write("-" * len(text) + "\n")
    write(".. code-block:: none\n")


all_imports = {
    "ImportError": ("test_import_error", "test_import_error"),
    "TypeError - 1: must be str, not int": ("test_type_error", "test_type_error1"),
    "TypeError - 1a: must be str, not list": ("test_type_error", "test_type_error1a"),
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
                        result = getattr(mod, function)()
                        write(result)
                except Exception:
                    friendly_traceback.explain()
