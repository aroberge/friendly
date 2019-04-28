"""Common information so that all traceback generating scripts
   create files in the same format.

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
    "SyntaxError - Assign to keyword": "syntax.raise_syntax_error1",
    "SyntaxError - Missing colon 1": "syntax.raise_syntax_error2",
    "SyntaxError - Missing colon 2": "syntax.raise_syntax_error3",
    "SyntaxError - elif, not else if": "syntax.raise_syntax_error4",
    "SyntaxError - elif, not elseif": "syntax.raise_syntax_error5",
    "SyntaxError - malformed def statment - 1": "syntax.raise_syntax_error6",
    "SyntaxError - malformed def statment - 2": "syntax.raise_syntax_error7",
    "SyntaxError - malformed def statment - 3": "syntax.raise_syntax_error8",
    "SyntaxError - can't assign to literal": "syntax.raise_syntax_error9",
    "SyntaxError - import X from Y": "syntax.raise_syntax_error10",
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
                    friendly_traceback.explain(*sys.exc_info(), redirect=None)
