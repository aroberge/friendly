import friendly


def test_Generic():
    d = {"a": 1, "b": 2}
    try:
        d["c"]
    except KeyError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "KeyError: 'c'" in result
    if friendly.get_lang() == "en":
        assert "that cannot be found is `c`." in result
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
        assert "that cannot be found is `42`." in result
    return result, message

if __name__ == "__main__":
    print(test_Generic()[0])
