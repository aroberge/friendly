# More complex example than needed - used for documentation
import friendly_traceback
import sys

b = 2


def outer():
    a = 1

    def inner():
        c = 3
        a = a + b + c
    inner()


def test_unbound_local_error():
    """Should raise UnboundLocalError"""

    try:
        outer()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "UnboundLocalError: local variable 'a' referenced" in result
    return result


if __name__ == "__main__":
    print(test_unbound_local_error())
