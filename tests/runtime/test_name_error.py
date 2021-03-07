import friendly
from math import *

def test_Generic():
    try:
        this = something
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'something' is not defined" in result
    if friendly.get_lang() == "en":
        assert "In your program, `something` is an unknown name." in result
    return result, message

x: 3

def test_Annotated_variable():
    try:
        y = x
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'x' is not defined" in result
    if friendly.get_lang() == "en":
        assert "x = 3" in result
    return result, message


def test_Synonym():
    try:
        a = i
    except Exception:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'i' is not defined" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `1j`" in result

    try:
        a = j
    except Exception:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'j' is not defined" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `1j`" in result

    nabs = 1
    try:
        x = babs(-1)
    except Exception as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'babs' is not defined" in result
    if friendly.get_lang() == "en":
        assert "perhaps you meant one of the following" in result

    try:
        cost  # wrote from math import * above
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'cost' is not defined" in result
    if friendly.get_lang() == "en":
        assert "perhaps you meant one of the following" in result
    return result, message

if __name__ == "__main__":
    print(test_Generic()[0])
