import friendly
expected_in_result = friendly.utils.expected_in_result


def test_Popitem_empty_dict():
    d = {}
    try:
        d.popitem()
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "popitem(): dictionary is empty" in result
    if friendly.get_lang() == "en":
        expected = "You tried to retrieve an item from `d` which is an empty `dict`."
        ok, diff = expected_in_result(expected, result)
        assert ok, diff
    return result, message


def test_Popitem_empty_ChainMap():
    from collections import ChainMap
    alpha = ChainMap({}, {})
    try:
        alpha.popitem()
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "popitem(): dictionary is empty" in result
    if friendly.get_lang() == "en":
        expected = "You tried to retrieve an item from `alpha` which is an empty `ChainMap`."
        ok, diff = expected_in_result(expected, result)
        assert ok, diff
    return result, message



def test_Generic_key_error():
    d = {"a": 1, "b": 2}
    try:
        d["c"]
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "KeyError: 'c'" in result
    if friendly.get_lang() == "en":
        expected = "The key `'c'` cannot be found in the dict `d`.\n"
        ok, diff = expected_in_result(expected, result)
        assert ok, diff
    return result, message


def test_ChainMap():
    from collections import ChainMap
    d = ChainMap({}, {})
    try:
        d.pop(42)
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "KeyError: 42" in result
    if friendly.get_lang() == "en":
        expected = "The key `42` cannot be found in `d`, an object of type `ChainMap`."
        ok, diff = expected_in_result(expected, result)
        assert ok, diff
    return result, message


def chain_map_string_by_mistake():
    from collections import ChainMap
    beta = ChainMap({(0, 0): "origin"}, {})
    try:
        beta.pop("(0, 0)")
    except KeyError as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "KeyError: '(0, 0)'" in result
    if friendly.get_lang() == "en":
        expected = "Did you convert `(0, 0)` into a string by mistake?"
        ok, diff = expected_in_result(expected, result)
        assert ok, diff


def test_String_by_mistake():

    chain_map_string_by_mistake()  # do not show in docs

    d = {(0, 0): "origin"}
    try:
        d["(0, 0)"]
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "KeyError: '(0, 0)'" in result
    if friendly.get_lang() == "en":
        expected = "Did you convert `(0, 0)` into a string by mistake?"
        ok, diff = expected_in_result(expected, result)
        assert ok, diff
    return result, message



if __name__ == "__main__":
    print(test_Generic()[0])
