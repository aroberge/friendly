import friendly_traceback
import sys

friendly_traceback.set_lang('en')


def test_unbound_local_error():
    """Should raise UnboundLocalError"""
    a = 1

    def inner():
        a += 1

    try:
        inner()
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "UnboundLocalError: local variable 'a' referenced before assignment" in result
    return result


if __name__ == "__main__":
    print(test_unbound_local_error())
