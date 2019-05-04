import friendly_traceback
import sys


def test_type_error1():
    try:
        a = 'a'
        one = 1
        result = a + one
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: can only concatenate str" in result
    return result


if __name__ == "__main__":
    print(test_type_error1())
