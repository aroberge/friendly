import friendly_traceback
from math import *

def test_name_error():
    try:
        this = something
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "NameError: name 'something' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, `something` is an unknown name." in result
    return result, message

def test_name_error2():
    nabs = 1
    try:
        x = babs(-1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "NameError: name 'babs' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "perhaps you meant one of the following" in result
    return result, message

x: 3

def test_name_error3():
    try:
        y = x
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "NameError: name 'x' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "x = 3" in result
    return result, message

def test_name_error4():
    try:
        cost  # wrote from math import * above
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "NameError: name 'cost' is not defined" in result
    if friendly_traceback.get_lang() == "en":
        assert "perhaps you meant one of the following" in result
    return result, message

if __name__ == "__main__":
    print(test_name_error()[0])
