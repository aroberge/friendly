import friendly_traceback
import sys


class MyException(Exception):
    pass


def test_unknown_error():
    try:
        raise MyException("Some informative message")
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "Some informative message" in result
    return result


if __name__ == "__main__":
    print(test_unknown_error())
