import friendly_traceback


def test_recursion_error():
    def a():
        return a()
    try:
        a()
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "RecursionError" in result
    if friendly_traceback.get_lang() == "en":
        assert "too many times" in result
    return result


if __name__ == "__main__":
    print(test_recursion_error())
