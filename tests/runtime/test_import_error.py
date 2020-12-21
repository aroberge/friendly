import friendly_traceback


def test_Simple_import_error():
    try:
        from math import Pi
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `pi`" in result
    return result, message


def test_Circular_import():
    try:
        import circular_a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    # The actual message varies a lot depending on Python version.
    assert not "debug_warning" in result, "Internal error found."
    assert "ImportError" in result
    if friendly_traceback.get_lang() == "en":
        assert "what is known as a 'circular import'" in result

    return result, message


if __name__ == "__main__":
    print(test_Simple_import_error()[0])
