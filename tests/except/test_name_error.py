import friendly_traceback
from math import *

def test_name_error():
    try:
        cost  # wrote from math import * above
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'cost' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, the unknown name is 'cost'." in result
    return result

def test_name_error2():
    nabs = 1
    try:
        x = babs(-1)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'babs' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, the unknown name is 'babs'." in result
    return result


if __name__ == "__main__":
    print(test_name_error())
