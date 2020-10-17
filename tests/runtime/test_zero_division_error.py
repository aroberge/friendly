import friendly_traceback


def test_zero_division_error():
    try:
        1 / 0
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: division by zero" in result
    if friendly_traceback.get_lang() == "en":
        assert "A `ZeroDivisionError` occurs when" in result
    return result, message


def test_zero_division_error2():
    zero = 0
    try:
        1 % zero
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly_traceback.get_lang() == "en":
        assert "A `ZeroDivisionError` occurs when" in result
    return result, message


if __name__ == "__main__":
    print(test_zero_division_error()[0])
    print("-" * 60)
    print(test_zero_division_error2()[0])
