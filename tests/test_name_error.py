import friendly_traceback
import sys


def test_name_error():
    try:
        b = c
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'c' is not defined" in result
    return result


if __name__ == "__main__":
    print(test_name_error())
