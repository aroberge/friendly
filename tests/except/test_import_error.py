import friendly_traceback


def test_import_error():
    try:
        from math import Pi
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly_traceback.get_lang() == "en":
        assert "The object that could not be imported is `Pi`." in result
    return result


if __name__ == "__main__":
    print(test_import_error())
