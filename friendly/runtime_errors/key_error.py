import sys

from ..my_gettext import current_lang, internal_error
from .. import info_variables
from .. import debug_helper
from .. import utils


def get_cause(value, frame, tb_data):
    try:
        return _get_cause(value, frame, tb_data)
    except Exception as e:
        debug_helper.log_error(e)
        return {"cause": internal_error(), "suggest": internal_error()}


def cannot_find_key(key):
    _ = current_lang.translate
    return _("In your program, the key that cannot be found is `{key}`.\n").format(
        key=key
    )


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    key = value.args[0]
    if "collections" in sys.modules:
        possible_cause = handle_chain_map_case(key)
        if possible_cause:
            return possible_cause

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, dict) and key not in obj:
            break
    else:
        return {"cause": cannot_find_key(key)}

    if isinstance(key, str):
        keys = [str(k) for k in obj.keys()]
        if key in keys:
            additional = _(
                "`{key}` is a string.\n"
                "There is a key of `{name}` whose string representation\n"
                "is identical to `{key}`.\n"
            ).format(key=key, name=name)
            hint = _("Did you convert '{key}' into a string by mistake?\n").format(
                key=key
            )
            return {"cause": cannot_find_key(key) + additional, "suggest": hint}

        string_keys = [k for k in obj.keys() if isinstance(k, str)]
        similar = utils.get_similar_words(key, string_keys)
        if len(similar) == 1:
            hint = _("Did you mean `{name}`?\n").format(name=similar[0])
            additional = _(
                "`{name}` is a key of `{dict_}` which is similar to `{key}`.\n"
            ).format(name=similar[0], dict_=name, key=key)
            return {"cause": cannot_find_key(key) + additional, "suggest": hint}

        if similar:
            hint = _("Did you mean `{name}`?\n").format(name=similar[0])
            additional = _(
                "`{dict_}` has some keys similar to `{key}` including:\n" "`{names}`\n"
            ).format(dict_=name, key=key, names=utils.list_to_string(similar))
            return {"cause": cannot_find_key(key) + additional, "suggest": hint}
    else:
        if str(key) in obj.keys():
            additional = _(
                "`{name}` contains a string key which is identical to `str({key})`.\n"
                "Perhaps you forgot to convert the key into a string.\n"
            ).format(name=name, key=key)
            hint = _("Did you forget to convert '{key}' into a string?\n").format(
                key=key
            )
            return {"cause": cannot_find_key(key) + additional, "suggest": hint}

    return {"cause": cannot_find_key(key)}


def handle_chain_map_case(key):
    """Missing keys in collections.ChainMap trigger a secondary exception with
    a different message. We process this message here so as to extract the
    correct value of the missing key."""
    import ast

    try:
        if not key.startswith("Key not found in the first mapping: "):
            return {}
    except Exception:
        return {}

    key = key.replace("Key not found in the first mapping: ", "", 1)
    if not (key.startswith("'") or key.startswith('"')):
        try:
            key = ast.literal_eval(key)
        except Exception:
            pass

    return {"cause": cannot_find_key(key)}
