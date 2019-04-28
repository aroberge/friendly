import friendly_traceback
import sys


def test_lookup_error():
    try:
        # LookupError is the base class for KeyError and IndexError.
        # It should normally not be raised by user code,
        # other than possibly codecs.lookup(), which is why we raise
        # it directly here for our example.
        raise LookupError
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "LookupError" in result
    return result


if __name__ == "__main__":
    print(test_lookup_error())
