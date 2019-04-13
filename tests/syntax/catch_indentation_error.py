import friendly_traceback
import sys


def test_indentation_error1():
    try:
        try:
            from . import raise_indentation_error1  # for pytest
        except ImportError:
            import raise_indentation_error1  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "IndentationError: expected an indented block" in result
    return result


def test_indentation_error2():
    try:
        try:
            from . import raise_indentation_error2  # for pytest
        except ImportError:
            import raise_indentation_error2  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "IndentationError: unexpected indent" in result
    return result


def test_indentation_error3():
    try:
        try:
            from . import raise_indentation_error3  # for pytest
        except ImportError:
            import raise_indentation_error3  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "IndentationError: unindent does not match any outer indentation level"
        in result
    )  # noqa
    return result


if __name__ == "__main__":
    print("-" * 50)
    print("   First test")
    print("-" * 50)
    print(test_indentation_error1())

    print("\n" + "-" * 50)
    print("   Second test")
    print("-" * 50)
    print(test_indentation_error2())

    print("\n" + "-" * 50)
    print("   Third test")
    print("-" * 50)
    print(test_indentation_error3())
