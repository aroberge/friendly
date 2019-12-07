import friendly_traceback


def test_key_error():
    d = {'a': 1, 'b': 2}
    try:
        d['c']
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "KeyError: 'c'" in result
    assert "that cannot be found is 'c'." in result
    return result


if __name__ == "__main__":
    print(test_key_error())
