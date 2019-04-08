import friendly_traceback
import sys


def test_name_error():
    try:
        from . import raise_name_error  # for pytest
    except ImportError:
        import raise_name_error

    try:
        raise_name_error.test()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'c' is not defined" in result
    return result


def test_flush():
    try:
        from . import raise_name_error  # for pytest
    except ImportError:
        import raise_name_error

    try:
        raise_name_error.test()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output(flush=False)
    assert "NameError: name 'c' is not defined" in result
    result = friendly_traceback.get_output()  # flushes
    result = friendly_traceback.get_output()  # returns empty list
    assert not result


if __name__ == "__main__":
    result = test_name_error()
    print(result)
