import friendly_traceback
import sys


def test_tab_error1():
    try:
        from . import raise_tab_error1  # for pytest
    except ImportError:
        import raise_tab_error1

    try:
        raise_tab_error1.test_tab_error1()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "TabError: inconsistent use of tabs and spaces in indentation" in result
    return result


def no_pytest_tab_error2():
    try:
        import raise_tab_error2
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "TabError: inconsistent use of tabs and spaces in indentation" in result
    return result


if __name__ == "__main__":
    result = test_tab_error1()
    print(result)
    print("-"*50)
    result = no_pytest_tab_error2()
    print(result)
