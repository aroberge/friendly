"""Getting specific information for ImportError"""

import re
import sys

from ..my_gettext import current_lang, please_report
from ..utils import get_similar_words, list_to_string, RuntimeMessageParser
from ..path_info import path_utils
from .. import debug_helper

parser = RuntimeMessageParser()


@parser.add
def partially_initialized_module(message, _frame, tb_data):
    # Python 3.8+
    pattern = re.compile(
        r"cannot import name '(.*)' from partially initialized module '(.*)'"
    )
    match = re.search(pattern, message)
    if not match:
        return {}
    if "circular import" in message:
        return cannot_import_name_from(
            match.group(1), match.group(2), tb_data, add_circular_hint=False
        )
    # I thought I saw such a case where "circular import" was not added
    # but have not been able to find it again.
    return cannot_import_name_from(
        match.group(1), match.group(2), tb_data
    )  # pragma: no cover


@parser.add
def _cannot_import_name_from(message, _frame, tb_data):
    # Python 3.7+
    pattern = re.compile(r"cannot import name '(.*)' from '(.*)'")
    match = re.search(pattern, message)
    if not match:
        return {}
    return cannot_import_name_from(match.group(1), match.group(2), tb_data)


@parser.add
def _cannot_import_name(message, _frame, tb_data):
    # Python 3.6 does not give us more information
    pattern = re.compile(r"cannot import name '(.*)'")
    match = re.search(pattern, message)
    if not match:  # pragma: no cover
        debug_helper.log("New case to consider.")
        return {}
    return cannot_import_name(match.group(1), tb_data)


def cannot_import_name_from(name, module, tb_data, add_circular_hint=True):
    _ = current_lang.translate

    hint = None
    circular_info = None

    modules_imported = extract_import_data_from_traceback(tb_data)
    if modules_imported:
        circular_info = find_circular_import(modules_imported)
        if circular_info and add_circular_hint:
            hint = _("You have a circular import.\n")
            # Python 3.8+ adds a similar hint on its own.

    cause = _(
        "The object that could not be imported is `{name}`.\n"
        "The module or package where it was \n"
        "expected to be found is `{module}`.\n"
    ).format(name=name, module=module)

    if circular_info:
        if hint is None:
            return {"cause": cause + "\n" + circular_info}

        return {"cause": cause + "\n" + circular_info, "suggest": hint}

    if not add_circular_hint:  # pragma: no cover
        debug_helper.log("New case to consider")
        return {
            "cause": cause
            + "\n"
            + _(
                "Python indicated that you have a circular import.\n"
                "This can occur if executing the code in module 'A'\n"
                "results in executing the code in module 'B' where\n"
                "an attempt to import a name from module 'A' is made\n"
                "before the execution of the code in module 'A' had been completed.\n"
            )
        }

    try:
        mod = sys.modules[module]
    except Exception:  # noqa  # pragma: no cover
        cause += "\n" + _(
            "Inconsistent state: `'{module}'` was apparently not imported.\n"
            "As a result, no further analysis can be done.\n"
        ).format(module=module)
        return {"cause": cause}

    similar = get_similar_words(name, dir(mod))
    if not similar:
        return {"cause": cause}

    if len(similar) == 1:
        hint = _("Did you mean `{name}`?\n").format(name=similar[0])
        cause = _(
            "Perhaps you meant to import `{correct}` (from `{module}`) "
            "instead of `{typo}`\n"
        ).format(correct=similar[0], typo=name, module=module)
    else:
        candidates = list_to_string(similar)
        hint = _("Did you mean one of the following: `{names}`?\n").format(
            names=candidates
        )
        cause = _(
            "Instead of trying to import `{typo}` from `{module}`, \n"
            "perhaps you meant to import one of \n"
            "the following names which are found in module `{module}`:\n"
            "`{candidates}`\n"
        ).format(candidates=candidates, typo=name, module=module)

    return {"cause": cause, "suggest": hint}


def cannot_import_name(name, tb_data):
    # Python 3.6 does not give us the name of the module
    _ = current_lang.translate
    pattern = re.compile(r"from (.*) import")
    match = re.search(pattern, tb_data.bad_line)

    if not match:  # pragma: no cover
        debug_helper.log("New case to consider.")
        return {
            "cause": _("The object that could not be imported is `{name}`.\n").format(
                name=name
            )
            + please_report()
        }

    return cannot_import_name_from(name, match.group(1), tb_data)


def extract_import_data_from_traceback(tb_data):
    """Attempts to extract the list of imported modules from the traceback information"""
    pattern_file = re.compile(r'^File "(.*)", line', re.M)
    pattern_from = re.compile(r"^from (.*) import", re.M)
    pattern_import = re.compile(r"^import (.*)", re.M)
    modules_imported = []
    tb_lines = tb_data.simulated_python_traceback.split("\n")
    current_file = ""
    for line in tb_lines:
        line = line.strip()
        match_file = re.search(pattern_file, line)
        match_from = re.search(pattern_from, line)
        match_import = re.search(pattern_import, line)

        if match_file:
            current_file = path_utils.shorten_path(match_file.group(1))
        elif match_from or match_import:
            if match_from:
                modules_imported.append((current_file, match_from.group(1)))
            else:
                module = match_import.group(1)
                if "," in module:  # multiple modules imported on same line
                    modules = module.split(",")
                    for mod in modules:
                        modules_imported.append(
                            (current_file, mod.replace("(", "").strip())
                        )
                else:
                    modules_imported.append((current_file, module))
            current_file = ""

    return modules_imported


def find_circular_import(modules_imported):
    """This attempts to find circular imports."""
    _ = current_lang.translate

    last_file, last_module = modules_imported[-1]

    for file, module in modules_imported[:-1]:
        if module == last_module:
            return _(
                "The problem was likely caused by what is known as a 'circular import'.\n"
                "First, Python imported and started executing the code in file\n"
                "   '{file}'.\n"
                "which imports module `{last_module}`.\n"
                "During this process, the code in another file,\n"
                "   '{last_file}'\n"
                "was executed. However in this last file, an attempt was made\n"
                "to import the original module `{last_module}`\n"
                "a second time, before Python had completed the first import.\n"
            ).format(
                file=file, last_file=last_file, module=module, last_module=last_module
            )
