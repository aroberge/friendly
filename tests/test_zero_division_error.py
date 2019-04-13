import friendly_traceback
import sys


def test_zero_division_error():
    try:
        1 / 0
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: division by zero" in result
    return result


def test_zero_division_error2():
    try:
        1 % 0
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "ZeroDivisionError: integer division or modulo by zero" in result
    return result


if __name__ == "__main__":
    print(test_zero_division_error())
    print("-"*60)
    print(test_zero_division_error2())
