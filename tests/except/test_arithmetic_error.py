import friendly_traceback


def test_arithmetic_error():
    try:
        # I am not aware of any way in which this error is raised directly
        # Usually, a subclass such as ZeroDivisionError, etc., would
        # likely be raised.
        raise ArithmeticError
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ArithmeticError" in result
    if friendly_traceback.get_lang() == "en":
        assert "ArithmeticError is the base class" in result
    return result


if __name__ == "__main__":
    print(test_arithmetic_error())
