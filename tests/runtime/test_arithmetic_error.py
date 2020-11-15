import friendly_traceback


def test_arithmetic_error():
    try:
        # I am not aware of any way in which this error is raised directly
        # Usually, a subclass such as ZeroDivisionError, etc., would
        # likely be raised.
        raise ArithmeticError
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "ArithmeticError" in result
    if friendly_traceback.get_lang() == "en":
        assert "`ArithmeticError` is the base class" in result
    return result, message


if __name__ == "__main__":
    print(test_arithmetic_error()[0])
