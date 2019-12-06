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
    "SyntaxError - can't assign to literal - 2": "syntax.raise_syntax_error9a",
    "SyntaxError - import X from Y": "syntax.raise_syntax_error10",
    "SyntaxError - EOL while scanning string literal": "syntax.raise_syntax_error11",
    "SyntaxError - assignment to keyword (None)": "syntax.raise_syntax_error12",
    "SyntaxError - assignment to keyword (__debug__)": "syntax.raise_syntax_error13",
    "SyntaxError - unmatched closing parenthesis": "syntax.raise_syntax_error14",
    "SyntaxError - unclosed parenthesis": "syntax.raise_syntax_error15",
    "SyntaxError - unclosed parenthesis - 2": "syntax.raise_syntax_error15a",
    "SyntaxError - mismatched brackets": "syntax.raise_syntax_error16",
    "SyntaxError - mismatched brackets - 2": "syntax.raise_syntax_error16a",
    "SyntaxError - print is a function": "syntax.raise_syntax_error17",
    "SyntaxError - Python keyword as function name": "syntax.raise_syntax_error18",
    "SyntaxError - break outside loop": "syntax.raise_syntax_error19",
    "SyntaxError - continue outside loop": "syntax.raise_syntax_error20",
    "SyntaxError - quote inside a string": "syntax.raise_syntax_error21",
    "SyntaxError - missing comma in a dict": "syntax.raise_syntax_error22",
    "SyntaxError - missing comma in a set": "syntax.raise_syntax_error23",
    "SyntaxError - missing comma in a list": "syntax.raise_syntax_error24",
    "SyntaxError - missing comma in a tuple": "syntax.raise_syntax_error25",
    "SyntaxError - missing comma between function args": "syntax.raise_syntax_error26",
    "SyntaxError - can't assign to function call - 1": "syntax.raise_syntax_error27",
    "SyntaxError - can't assign to function call - 2": "syntax.raise_syntax_error28",
    "SyntaxError - used equal sign instead of colon": "syntax.raise_syntax_error29",
    "SyntaxError - non-default argument follows default argument": "syntax.raise_syntax_error30",
    "SyntaxError - positional argument follows keyword argument": "syntax.raise_syntax_error31",
    "SyntaxError - f-string: unterminated string": "syntax.raise_syntax_error32",
    "SyntaxError - unclosed bracket": "syntax.raise_syntax_error33",
    "SyntaxError - unexpected EOF while parsing": "syntax.raise_syntax_error34",
    "SyntaxError - name is parameter and global": "syntax.raise_syntax_error35",
    "SyntaxError - keyword as attribute": "syntax.raise_syntax_error36",
    "SyntaxError - content passed continuation line character": "syntax.raise_syntax_error37",
    "SyntaxError - keyword can't be an expression": "syntax.raise_syntax_error38",
    "SyntaxError - invalid character in identifier": "syntax.raise_syntax_error39",
    "SyntaxError - keyword cannot be argument in def - 1": "syntax.raise_syntax_error40",
    "SyntaxError - keyword cannot be argument in def - 2": "syntax.raise_syntax_error41",
    "SyntaxError - keyword cannot be argument in def - 3": "syntax.raise_syntax_error42",
    "SyntaxError - keyword cannot be argument in def - 4": "syntax.raise_syntax_error43",
}

if sys.version_info < (3, 8):
    all_imports[
        "Walrus operator does not exist - yet"
    ] = "syntax.raise_syntax_error_walrus"


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


print("Number of cases in trb_syntax_common.py: ", len(all_imports))
