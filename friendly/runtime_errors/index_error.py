"""Getting specific information for IndexError"""

import ast
import re

import pure_eval

from .. import debug_helper
from .. import info_variables
from ..my_gettext import current_lang, no_information, internal_error


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:  # pragma: no cover
        debug_helper.log_error(e)
        return {"cause": internal_error(e)}


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    message = str(value)

    pattern = re.compile(r"(.*) index out of range")
    match = re.search(pattern, message)
    if match:
        return index_out_of_range(match.group(1), frame, tb_data)

    debug_helper.log("New IndexError case to consider.")  # pragma: no cover
    return {"cause": no_information()}  # pragma: no cover


def index_out_of_range(obj_type, frame, tb_data):
    _ = current_lang.translate

    # first, try to identify object
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, sequence in all_objects["name, obj"]:
        truncated = tb_data.bad_line.replace(name, "", 1)
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:  # pragma: no cover
        debug_helper.log("Cannot identify object in index_out_of_range().")
        return {}

    try:
        node = tb_data.node
    except Exception:  # noqa # pragma: no cover
        debug_helper.log("node does not exist in index_out_of_range()")
        return {}

    if not (node and isinstance(node, ast.Subscript)):  # pragma: no cover
        debug_helper.log("node is not Subscript in index_out_of_range().")
        return {}

    length = len(sequence)
    evaluator = pure_eval.Evaluator.from_frame(frame)
    # The information that we want may differ for different
    # Python versions
    try:
        index = evaluator[node.slice.value]
    except Exception:  # noqa
        try:
            index = evaluator[node.slice]
        except Exception:  # noqa  # pragma: no cover
            debug_helper.log("Unknown index: new case to consider.")
            cause = _(
                "You have tried to get an item from `{name}`,\n"
                "{obj_type} of length `{length}`, by using a value for the index\n"
                "that I cannot determine but which is not allowed.\n"
            ).format(
                name=name, length=length, obj_type=info_variables.convert_type(obj_type)
            )
            return {"cause": cause}

    cause = _(
        "You have tried to get the item with index `{index}` of `{name}`,\n"
        "{obj_type} of length `{length}`.\n"
    ).format(
        index=index,
        name=name,
        length=length,
        obj_type=info_variables.convert_type(obj_type),
    )

    if length != 0:
        cause += _(
            "The valid index values of `{name}` are integers ranging from\n"
            "`{min}` to `{max}`.\n"
        ).format(name=name, min=-length, max=length - 1)
        if index == length:
            hint = _(
                "Remember: the first item of {obj_type} is not at index 1 but at index 0.\n"
            ).format(obj_type=info_variables.convert_type(obj_type))
            return {"cause": cause, "suggest": hint}
    else:
        hint = _("`{name}` contains no item.\n").format(name=name)
        cause = _(
            "You have tried to get the item with index `{index}` of `{name}`,\n"
            "{obj_type} which contains no item.\n"
        ).format(index=index, name=name, obj_type=info_variables.convert_type(obj_type))
        return {"cause": cause, "suggest": hint}

    return {"cause": cause}
