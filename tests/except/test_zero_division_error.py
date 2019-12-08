import friendly_traceback


def test_zero_division_error():
    try:
        1 / 0
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: division by zero" in result
    if friendly_traceback.get_lang() == 'en':
        assert "A ZeroDivisionError occurs when" in result
    return result


def test_zero_division_error2():
    zero = 0
    try:
        1 % zero
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly_traceback.get_lang() == 'en':
        assert "A ZeroDivisionError occurs when" in result
    return result


if __name__ == "__main__":
    print(test_zero_division_error())
    print("-"*60)
    print(test_zero_division_error2())
