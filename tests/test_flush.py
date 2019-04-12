import friendly_traceback
import sys


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
    result1 = friendly_traceback.get_output()  # flushes
    result1 = friendly_traceback.get_output()  # returns empty string
    assert not result1
    return result, result1


if __name__ == "__main__":
    result, result1 = test_flush()
    print("Before flush:\n", "-"*50)
    print(result)
    print("="*50, "\nAfter flush:\n", "-"*50)
    print(result1)
