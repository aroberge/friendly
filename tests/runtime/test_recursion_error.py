import friendly_traceback


def test_Generic():
    def a():
        return a()
    try:
        a()
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "RecursionError" in result
    if friendly_traceback.get_lang() == "en":
        assert "too many times" in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
