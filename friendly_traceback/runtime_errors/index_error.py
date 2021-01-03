"""Getting specific information for IndexError"""

import ast
import re

import pure_eval

from .. import debug_helper
from .. import info_variables
from ..my_gettext import current_lang


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:
        debug_helper.log_error(e)
        return None, None


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    message = str(value)

    cause = _(
        "No information is known about this exception.\n"
        "Please report this example to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
    )
    hint = None  # unused for now

    pattern = re.compile(r"(.*) index out of range")
    match = re.search(pattern, message)
    if match:
        cause, hint = index_out_of_range(match.group(1), frame, tb_data)
    return cause, hint


def index_out_of_range(obj_type, frame, tb_data):
    _ = current_lang.translate
    cause = hint = None

    # first, try to identify object
    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, sequence in all_objects["name, obj"]:
        truncated = tb_data.bad_line.replace(name, "", 1)
        if truncated.startswith("[") and truncated.endswith("]"):
            break
    else:
        debug_helper.log("Cannot identify object in index_out_of_range().")
        return cause, hint

    try:
        node = tb_data.node
    except Exception:
        debug_helper.log("node does not exist in index_out_of_range()")
        return cause, hint

    if not (node and isinstance(node, ast.Subscript)):
        debug_helper.log("node is not Subscript in index_out_of_range().")
        return cause, hint

    length = len(sequence)
    evaluator = pure_eval.Evaluator.from_frame(frame)
    try:
        index = evaluator[node.slice.value]
    except TypeError:  # Python 3.10.0a3
        index = evaluator[node.slice]

    cause = _(
        "You have tried to get the item with index `{index}` of `{name}`,\n"
        "{obj_type} of length `{length}`.\n"
    ).format(
        index=index,
        name=name,
        length=length,
        obj_type=info_variables.convert_type(obj_type),
    )

    if index == length:
        cause += _("The largest valid index of `{name}` is `{index}`.\n").format(
            name=name, index=length - 1
        )
        hint = _("Remember: the first item of {obj_type} is at index 0.\n").format(
            obj_type=info_variables.convert_type(obj_type)
        )

    return cause, hint
