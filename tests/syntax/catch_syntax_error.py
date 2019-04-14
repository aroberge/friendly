import friendly_traceback
import sys

# There has to be a better way to write these tests, saving on the copy-pasting.
# We do not add more specific information as the result
# of these is displayed fully in the documentation.


def test_syntax_error1():
    try:
        try:
            from . import raise_syntax_error1  # for pytest
        except ImportError:
            import raise_syntax_error1  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error2():
    try:
        try:
            from . import raise_syntax_error2  # for pytest
        except ImportError:
            import raise_syntax_error2  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error3():
    try:
        try:
            from . import raise_syntax_error3  # for pytest
        except ImportError:
            import raise_syntax_error3  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error4():
    try:
        try:
            from . import raise_syntax_error4  # for pytest
        except ImportError:
            import raise_syntax_error4  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error5():
    try:
        try:
            from . import raise_syntax_error5  # for pytest
        except ImportError:
            import raise_syntax_error5  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error6():
    try:
        try:
            from . import raise_syntax_error6  # for pytest
        except ImportError:
            import raise_syntax_error6  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result


def test_syntax_error7():
    try:
        try:
            from . import raise_syntax_error7  # for pytest
        except ImportError:
            import raise_syntax_error7  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result

def test_syntax_error5():
    try:
        try:
            from . import raise_syntax_error5  # for pytest
        except ImportError:
            import raise_syntax_error5  # noqa
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "SyntaxError" in result
    return result

if __name__ == "__main__":
    print("-" * 50)
    print("   First test")
    print("-" * 50)
    print(test_syntax_error1())
