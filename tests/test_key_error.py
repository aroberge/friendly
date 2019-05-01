import friendly_traceback
import sys


def test_key_error():
    d = {'a': 1, 'b': 2}
    try:
        d['c']
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "KeyError" in result
    return result


if __name__ == "__main__":
    print(test_key_error())
