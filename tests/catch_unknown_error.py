import friendly_traceback
import sys


def test_unknown_error():
    try:
        from . import raise_unknown_error  # for pytest
    except ImportError:
        import raise_unknown_error

    try:
        raise_unknown_error.test()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "Some informative message" in result
    return result


if __name__ == "__main__":
    result = test_unknown_error()
    print(result)
