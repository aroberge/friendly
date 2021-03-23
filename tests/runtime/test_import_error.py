import friendly


def test_Simple_import_error():
    try:
        from math import Pi
    except ImportError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `pi`" in result
    return result, message


def test_Circular_import():
    try:
        import circular_a
    except ImportError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    # The actual message varies a lot depending on Python version.

    if friendly.get_lang() == "en":
        assert "what is known as a 'circular import'" in result

    return result, message


if __name__ == "__main__":
    print(test_Simple_import_error()[0])
