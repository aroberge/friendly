"""Common information so that all traceback generating scripts
   create files in the same format.

"""
import os
import sys
from contextlib import redirect_stderr

import friendly_traceback


def write(text):
    sys.stderr.write(text + "\n")


def make_title(text, format="pre", underline="-"):
    if format == "pre":
        write("\n" + text)
        write(underline * len(text) + "\n")
        if underline == "~":
            write(".. code-block:: none\n")
    elif format == "markdown_docs":
        if underline == "-":
            write("\n---\n")
            write("## " + text)
        else:
            write("### " + text)
    else:
        print("Unsupported format: ", format)
        sys.exit()


cur_dir = os.getcwd()
sys.path.append(os.path.join(cur_dir, "runtime"))

save_messages = {}

test_files = [
    "test_arithmetic_error",
    "test_attribute_error",
    "test_file_not_found_error",
    "test_import_error",
    "test_index_error",
    "test_key_error",
    "test_lookup_error",
    "test_module_not_found_error",
    "test_name_error",
    "test_overflow_error",
    "test_recursion_error",
    "test_type_error",
    "test_unbound_local_error",
    "test_unknown_error",
    "test_value_error",
    "test_zero_division_error",
]


def create_tracebacks(target, intro_text, format="pre", messages=None):
    nb_cases = 0
    with open(target, "w", encoding="utf8") as out:
        with redirect_stderr(out):
            write(intro_text)

            for filename in test_files:  # no .py
                try:
                    mod = __import__(filename)
                    error_name = filename.replace("test_", "").replace("_", " ")
                    error_name = error_name.title().replace(" ", "")
                    make_title(error_name, format=format)
                    for name in dir(mod):
                        if name.startswith("test"):
                            function = getattr(mod, name)
                            if callable(function):
                                result, message = function()
                                title = name[5:].replace("_", " ")
                                save_messages[title] = message
                                make_title(title, format=format, underline="~")
                                write(result)
                                nb_cases += 1
                except Exception as e:
                    friendly_traceback.explain_traceback()

    print("    Number of cases in trb_common.py: ", nb_cases)
    if messages:
        with open(messages, "w", encoding="utf8") as out:
            out.write("messages = {\n")
            for key in save_messages:
                out.write(f"    {repr(key)}: {repr(save_messages[key])},\n")
            out.write("}\n")
