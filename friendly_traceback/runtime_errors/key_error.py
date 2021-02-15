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


def _get_cause(value, frame, tb_data):
    _ = current_lang.translate

    key = value.args[0]
    cannot_find = _(
        "In your program, the key that cannot be found is `{key}`.\n"
    ).format(key=key)

    all_objects = info_variables.get_all_objects(tb_data.bad_line, frame)
    for name, obj in all_objects["name, obj"]:
        if isinstance(obj, dict) and key not in obj:
            break
    else:
        return {"cause": cannot_find}

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
            return {"cause": cannot_find + additional, "suggest": hint}

        string_keys = [k for k in obj.keys() if isinstance(k, str)]
        similar = utils.get_similar_words(key, string_keys)
        if len(similar) == 1:
            hint = _("Did you mean `{name}`?\n").format(name=similar[0])
            additional = _(
                "`{name}` is a key of `{dict_}` which is similar to `{key}`.\n"
            ).format(name=similar[0], dict_=name, key=key)
            return {"cause": cannot_find + additional, "suggest": hint}
        elif similar:
            hint = _("Did you mean `{name}`?\n").format(name=similar[0])
            additional = _(
                "`{dict_}` has some keys similar to `{key}` including:\n" "`{names}`\n"
            ).format(dict_=name, key=key, names=utils.list_to_string(similar))
            return {"cause": cannot_find + additional, "suggest": hint}
    else:
        if str(key) in obj.keys():
            additional = _(
                "`{name}` contains a string key which is identical to `str({key})`.\n"
                "Perhaps you forgot to convert the key into a string.\n"
            ).format(name=name, key=key)
            hint = _("Did you forget to convert '{key}' into a string?\n").format(
                key=key
            )
            return {"cause": cannot_find + additional, "suggest": hint}

    return {"cause": cannot_find}
