"""Common information so that all traceback generating scripts
   create files in the same format.

"""
import os
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
    "IndentationError - 1: expected an indented block": "raise_indentation_error1",
    "IndentationError - 2: unexpected indent": "raise_indentation_error2",
    "IndentationError - 3: unindent does not match ...": "raise_indentation_error3",
    "TabError": "raise_tab_error",
    "SyntaxError - Assign to keyword": "raise_syntax_error1",
    "SyntaxError - Missing colon - 1": "raise_syntax_error2",
    "SyntaxError - Missing colon - 2": "raise_syntax_error3",
    "SyntaxError - elif, not else if": "raise_syntax_error4",
    "SyntaxError - elif, not elseif": "raise_syntax_error5",
    "SyntaxError - malformed def statment - 1": "raise_syntax_error6",
    "SyntaxError - malformed def statment - 2": "raise_syntax_error7",
    "SyntaxError - malformed def statment - 3": "raise_syntax_error8",
    "SyntaxError - can't assign to literal - 1": "raise_syntax_error9",
    "SyntaxError - can't assign to literal - 2": "raise_syntax_error10",
    "SyntaxError - can't assign to literal - 3": "raise_syntax_error52",
    "SyntaxError - can't assign to literal - 4": "raise_syntax_error53",
    "SyntaxError - can't assign to literal - 5": "raise_syntax_error54",
    "SyntaxError - import X from Y": "raise_syntax_error11",
    "SyntaxError - EOL while scanning string literal": "raise_syntax_error12",
    "SyntaxError - assignment to keyword (None)": "raise_syntax_error13",
    "SyntaxError - assignment to keyword (__debug__)": "raise_syntax_error14",
    "SyntaxError - unmatched closing parenthesis": "raise_syntax_error15",
    "SyntaxError - unclosed parenthesis- 1": "raise_syntax_error16",
    "SyntaxError - unclosed parenthesis - 2": "raise_syntax_error17",
    "SyntaxError - mismatched brackets": "raise_syntax_error18",
    "SyntaxError - mismatched brackets - 2": "raise_syntax_error19",
    "SyntaxError - print is a function": "raise_syntax_error20",
    "SyntaxError - Python keyword as function name": "raise_syntax_error21",
    "SyntaxError - break outside loop": "raise_syntax_error22",
    "SyntaxError - continue outside loop": "raise_syntax_error23",
    "SyntaxError - quote inside a string": "raise_syntax_error24",
    "SyntaxError - missing comma in a dict": "raise_syntax_error25",
    "SyntaxError - missing comma in a set": "raise_syntax_error26",
    "SyntaxError - missing comma in a list": "raise_syntax_error27",
    "SyntaxError - missing comma in a tuple": "raise_syntax_error28",
    "SyntaxError - missing comma between function args": "raise_syntax_error29",
    "SyntaxError - can't assign to function call - 1": "raise_syntax_error30",
    "SyntaxError - can't assign to function call - 2": "raise_syntax_error31",
    "SyntaxError - used equal sign instead of colon": "raise_syntax_error32",
    "SyntaxError - non-default argument follows default argument": "raise_syntax_error33",
    "SyntaxError - positional argument follows keyword argument": "raise_syntax_error34",
    "SyntaxError - f-string: unterminated string": "raise_syntax_error35",
    "SyntaxError - unclosed bracket": "raise_syntax_error36",
    "SyntaxError - unexpected EOF while parsing": "raise_syntax_error37",
    "SyntaxError - name is parameter and global": "raise_syntax_error38",
    "SyntaxError - keyword as attribute": "raise_syntax_error39",
    "SyntaxError - content passed continuation line character": "raise_syntax_error40",
    "SyntaxError - keyword can't be an expression": "raise_syntax_error41",
    "SyntaxError - invalid character in identifier": "raise_syntax_error42",
    "SyntaxError - keyword cannot be argument in def - 1": "raise_syntax_error43",
    "SyntaxError - keyword cannot be argument in def - 2": "raise_syntax_error44",
    "SyntaxError - keyword cannot be argument in def - 3": "raise_syntax_error45",
    "SyntaxError - keyword cannot be argument in def - 4": "raise_syntax_error46",
    "SyntaxError - delete function call": "raise_syntax_error47",
    "SyntaxError - assigned prior to global declaration": "raise_syntax_error48",
    "SyntaxError - used prior to global declaration": "raise_syntax_error49",
    "SyntaxError - assigned prior to nonlocal declaration": "raise_syntax_error5-",
    "SyntaxError - used prior to nonlocal declaration": "raise_syntax_error51",
    "SyntaxError - named assignment with Python constant": "raise_syntax_error55",
    "SyntaxError - assignment to operator": "raise_syntax_error56",
    "SyntaxError - using the backquote character": "raise_syntax_error57",
    "SyntaxError - assign to generator expression": "raise_syntax_error58",
    "SyntaxError - assign to conditional expression": "raise_syntax_error59",
    "SyntaxError - name is parameter and nonlocal": "raise_syntax_error60",
    "SyntaxError - name is global and nonlocal": "raise_syntax_error61",
    "SyntaxError - nonlocal variable not found": "raise_syntax_error62",
    "SyntaxError - nonlocal variable not found at module level": "raise_syntax_error63",
    "SyntaxError - keyword arg only once in function definition": "raise_syntax_error64",
    "SyntaxError - keyword arg only once in function call": "raise_syntax_error65",
    "SyntaxError - unexpected EOF while parsing 2": "raise_syntax_error66",
    "SyntaxError - print is a function 2": "raise_syntax_error67",
    "SyntaxError - copy/paste from interpreter": "raise_syntax_error68",
    "SyntaxError - Using pip from interpreter": "raise_syntax_error69",
    "SyntaxError - Using pip from interpreter 2": "raise_syntax_error70",
    "SyntaxError - dot followed by parenthesis": "raise_syntax_error71",
    "SyntaxError - cannot assign to f-string": "raise_syntax_error72",
    "SyntaxError - raising multiple exceptions": "raise_syntax_error73",
}

if sys.version_info < (3, 8):
    all_imports["Walrus operator does not exist - yet"] = "raise_syntax_error_walrus"

cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, "syntax"))


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
