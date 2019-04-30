import friendly_traceback
import sys


def test_unbound_local_error():
    """Should raise UnboundLocalError"""
    a = 1
    b = 2

    def inner():
        c = 3
        a = a + b + c

    try:
        inner()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "UnboundLocalError: local variable 'a' referenced before assignment" in result
    return result


if __name__ == "__main__":
    print(test_unbound_local_error())
