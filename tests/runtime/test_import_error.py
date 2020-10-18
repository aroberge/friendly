import friendly_traceback


def test_import_error():
    try:
        from math import Pi
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `pi`" in result
    return result, message


if __name__ == "__main__":
    print(test_import_error()[0])
