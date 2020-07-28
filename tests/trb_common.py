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


# The format of each item of the dict below is:
# ExceptionClass - optional heading:  (file, test_function)
#
# When a given exception class has more than one cases,
# the optional heading part hast to be added since each dict item must have
# a unique key. It can also be helpful to quickly identify if a particular
# case is included.


all_imports = {
    "ArithmeticError": ("test_arithmetic_error", "test_arithmetic_error"),
    "AttributeError - class attribute": ("test_attribute_error", "test_attribute_error"),
    "AttributeError - typo in module attribute": (
        "test_attribute_error",
        "test_misspelled_module_attribute",
    ),
    "AttributeError - typo in module attribute 2": (
        "test_attribute_error",
        "test_misspelled_module_attribute_2",
    ),
    "FileNotFoundError": ("test_file_not_found_error", "test_file_not_found_error"),
    "ImportError": ("test_import_error", "test_import_error"),
    "KeyError": ("test_key_error", "test_key_error"),
    "LookupError": ("test_lookup_error", "test_lookup_error"),
    "IndexError - short tuple": ("test_index_error", "test_index_error1"),
    "IndexError - long list": ("test_index_error", "test_index_error2"),
    "ModuleNotFoundError": (
        "test_module_not_found_error",
        "test_module_not_found_error",
    ),
    "NameError": ("test_name_error", "test_name_error"),
    "OverflowError": ("test_overflow_error", "test_overflow_error"),
    "TypeError - 1: concatenate two different types": (
        "test_type_error",
        "test_type_error1",
    ),
    "TypeError - 1a: concatenate two different types": (
        "test_type_error",
        "test_type_error1a",
    ),
    "TypeError - 1b: concatenate two different types": (
        "test_type_error",
        "test_type_error1b",
    ),
    "TypeError - 2: unsupported operand type(s) for +": (
        "test_type_error",
        "test_type_error2",
    ),
    "TypeError - 2a: unsupported operand type(s) for +=": (
        "test_type_error",
        "test_type_error2a",
    ),
    "TypeError - 3: unsupported operand type(s) for -": (
        "test_type_error",
        "test_type_error3",
    ),
    "TypeError - 3a: unsupported operand type(s) for -=": (
        "test_type_error",
        "test_type_error3a",
    ),
    "TypeError - 4: unsupported operand type(s) for *": (
        "test_type_error",
        "test_type_error4",
    ),
    "TypeError - 4a: unsupported operand type(s) for ``*=``": (
        "test_type_error",
        "test_type_error4a",
    ),
    "TypeError - 5: unsupported operand type(s) for /": (
        "test_type_error",
        "test_type_error5",
    ),
    "TypeError - 5a: unsupported operand type(s) for /=": (
        "test_type_error",
        "test_type_error5a",
    ),
    "TypeError - 5b: unsupported operand type(s) for //": (
        "test_type_error",
        "test_type_error5b",
    ),
    "TypeError - 5c: unsupported operand type(s) for //=": (
        "test_type_error",
        "test_type_error5c",
    ),
    "TypeError - 6: unsupported operand type(s) for &": (
        "test_type_error",
        "test_type_error6",
    ),
    "TypeError - 6a: unsupported operand type(s) for &=": (
        "test_type_error",
        "test_type_error6a",
    ),
    "TypeError - 7: unsupported operand type(s) for **": (
        "test_type_error",
        "test_type_error7",
    ),
    "TypeError - 7a: unsupported operand type(s) for ``**=``": (
        "test_type_error",
        "test_type_error7a",
    ),
    "TypeError - 8: unsupported operand type(s) for >>": (
        "test_type_error",
        "test_type_error8",
    ),
    "TypeError - 8a: unsupported operand type(s) for >>=": (
        "test_type_error",
        "test_type_error8a",
    ),
    "TypeError - 9: unsupported operand type(s) for @": (
        "test_type_error",
        "test_type_error9",
    ),
    "TypeError - 9a: unsupported operand type(s) for @=": (
        "test_type_error",
        "test_type_error9a",
    ),
    "TypeError - 10: comparison between incompatible types": (
        "test_type_error",
        "test_type_error10",
    ),
    "TypeError - 11: bad operand type for unary +": (
        "test_type_error",
        "test_type_error11",
    ),
    "TypeError - 11a: bad operand type for unary -": (
        "test_type_error",
        "test_type_error11a",
    ),
    "TypeError - 11b: bad operand type for unary ~": (
        "test_type_error",
        "test_type_error11b",
    ),
    "TypeError - 12: object does not support item assignment": (
        "test_type_error",
        "test_type_error12",
    ),
    "TypeError - 13: wrong number of positional arguments": (
        "test_type_error",
        "test_type_error13",
    ),
    "TypeError - 14: missing positional arguments": (
        "test_type_error",
        "test_type_error14",
    ),
    "TypeError - 15: tuple object is not callable": (
        "test_type_error",
        "test_type_error15",
    ),
    "TypeError - 15a: list object is not callable": (
        "test_type_error",
        "test_type_error15a",
    ),
    "UnboundLocalError": ("test_unbound_local_error", "test_unbound_local_error"),
    "Unknown exception": ("test_unknown_error", "test_unknown_error"),
    "ZeroDivisionError - 1": ("test_zero_division_error", "test_zero_division_error"),
    "ZeroDivisionError - 2": ("test_zero_division_error", "test_zero_division_error2"),
}

cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, "except"))


def create_tracebacks(target, intro_text):
    with open(target, "w", encoding="utf8") as out:
        with redirect_stderr(out):
            write(intro_text)

            for title in all_imports:
                function = None
                name, function = all_imports[title]
                make_title(title)
                try:
                    mod = __import__(name)
                    if function is not None:
                        result = getattr(mod, function)()
                        write(result)
                except Exception:
                    friendly_traceback.explain()


print("Number of cases in trb_common.py: ", len(all_imports))
