import friendly_traceback


def test_Division_operator():
    try:
        1 / 0
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "ZeroDivisionError: division by zero" in result
    if friendly_traceback.get_lang() == "en":
        assert "A `ZeroDivisionError` occurs when" in result
    return result, message


def test_Modulo_operator():
    zero = 0
    try:
        1 % zero
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly_traceback.get_lang() == "en":
        assert "A `ZeroDivisionError` occurs when" in result
    return result, message


if __name__ == "__main__":
    print(test_Divison_operator()[0])

