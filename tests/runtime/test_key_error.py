import friendly_traceback


def test_Generic():
    d = {"a": 1, "b": 2}
    try:
        d["c"]
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "KeyError: 'c'" in result
    if friendly_traceback.get_lang() == "en":
        assert "that cannot be found is `c`." in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
